require 'rexml/document'



=begin
generate <Context> element for tomcat server.xml
=end
def dspace_context ctxPath, ctxDocbase
	# path="/jspui" docBase="/home/undesa/apps/dspacesrv/webapps/jspui" debug="0" reloadable="true" cachingAllowed="false" allowLinking="true"/>
	ctxJsp = REXML::Element.new "Context"
	ctxJsp.add_attribute("path", ctxPath)
	ctxJsp.add_attribute("docBase", ctxDocbase)
	ctxJsp.add_attribute("debug", "0")
	ctxJsp.add_attribute("reloadable", "true")
	ctxJsp.add_attribute("cachingAllowed", "false")
	ctxJsp.add_attribute("allowLinking", "true")
	return ctxJsp
end



=begin 
Parse and Edit tomcat server.xml
=end
def update_tomcat_serverxml strFile

	File.open(strFile) do |serverxmlfile|
		serverxml = REXML::Document.new(serverxmlfile)
		#update the server port number 
		serverxml.root.elements['Service/Connector'].attributes['port'] = tomcat_port
		#add the dspace context elements to the host element
		serverhost = serverxml.root.elements['Service/Engine/Host']
		#<Context path="/jspui" docBase="/home/undesa/apps/dspacesrv/webapps/jspui" debug="0" 
		#reloadable="true" cachingAllowed="false" allowLinking="true"/>
		serverhost.add_element(dspace_context('/jspui' , "#{dspace_home}" + "/webapps/jspui"))
		serverhost.add_element(dspace_context('/xmlui' , "#{dspace_home}" + "/webapps/xmlui"))
		serverhost.add_element(dspace_context('/oai' , "#{dspace_home}" + "/webapps/oai"))
		fdspaceServerXml = File.open("#{dspace_server_xml}", "w")
		fdspaceServerXml.puts serverxml 
		dspaceXmlPath = fdspaceServerXml.path
		fdspaceServerXml.close
		end
end


def get_tomcat_admin_role 
	roleAdmin = REXML::Element.new "role"
	roleAdmin.add_attribute("rolename", "manager")
	return roleAdmin
end

def get_tomcat_admin_user 
	tomcatuser = REXML::Element.new "user"
	tomcatuser.add_attribute("username", "#{tomcat_admin_user}")
	tomcatuser.add_attribute("password", "#{tomcat_admin_password}")
	tomcatuser.add_attribute("roles", "manager")
	return tomcatuser
end

=begin 
Parse and Edit tomcat-users.xml
=end
def update_tomcat_usersxml strFile

	File.open(strFile) do |tomcatusersfile|
		usersxml = REXML::Document.new(tomcatusersfile)
		#update the server port number 
		tomcat_users_root = usersxml.elements['tomcat-users']
		tomcat_users_root.add_element(get_tomcat_admin_role())
		tomcat_users_root.add_element(get_tomcat_admin_user())
		fusersxml = File.open("#{dspace_tomcatusers_xml}", "w")
		fusersxml.puts usersxml
		usersXmlPath = fusersxml.path
		fusersxml.close
		end
end


