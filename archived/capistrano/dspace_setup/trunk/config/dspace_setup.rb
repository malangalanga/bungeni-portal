=begin
Sets up the pre-requisities for DSpace 
  -- Required System libraries
  -- User JVM (instead of using the system JVM)
  -- User tomcat application server
  -- Maven
  -- Ant
  -- Downloads and installs Postgres for the current user
=end


### Defines a sequence of tasks for installing bungeni from scratch ###

#### General Build Parameter #####

=begin
 Only the following 2 parameters need to be set by the user to customize
  this installation script for different computers
=end


namespace :dspace_setup do

    desc "Create DSpace db - drop and create it"
    task :create_db, :roles=> [:app] do
	[
	"#{pg_home}/bin/dropdb #{dspace_db_name} ;exit 0",
	"#{pg_home}/bin/createdb -E UNICODE #{dspace_db_name}"
	].each {|cmd| run cmd}	
    end

    desc "Configure DSpace cfg "
    task :setup_dspace_cfg, :roles=> [:app] do
        file = File.join(File.dirname(__FILE__), "templates", dspace_config_file)
        template = File.read(file)
        buffer = ERB.new(template).result(binding)
        put buffer, "#{dspace_download_dir}/#{dspace_install_dirname}/dspace/config/dspace.cfg", :mode => 0644
    end

    desc "Configure DSpace cfg "
    task :setup_dspace_dsrun, :roles=> [:app] do
        file = File.join(File.dirname(__FILE__), "templates", "dsrun.erb")
        template = File.read(file)
        buffer = ERB.new(template).result(binding)
        put buffer, "#{dspace_download_dir}/#{dspace_install_dirname}/dspace/bin/dsrun", :mode => 0754
    end

    desc "Configure Tomcat  "
    task :setup_tomcat_cfg, :roles=> [:app] do
	### 
	run "echo 'Setting up dspace with tomcat'"
	update_tomcat_serverxml tomcat_server_xml
	update_tomcat_usersxml tomcat_users_xml
	run "sleep 3"
	run "cp -f #{tomcat_server_xml} #{tomcat_server_xml}.`date +%F-%s`.bak"
	run "cp -f #{dspace_server_xml} #{tomcat_server_xml}"
	run "cp -f #{tomcat_users_xml} #{tomcat_users_xml}.`date +%F-%s`.bak"
	run "cp -f #{dspace_tomcatusers_xml} #{tomcat_users_xml}"

    end

    desc "Build DSpace with Maven "
    task :build_dspace, :roles=> [:app] do
	[
	"cd #{dspace_maven_root}/dspace && JAVA_HOME=#{java6_home} #{maven_home}/bin/mvn package",
	"cd #{dspace_maven_target_dir} && JAVA_HOME=#{java6_home} #{ant_home}/bin/ant fresh_install"
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant",
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant fresh_install"
	].each {|cmd| run cmd}	
    end

    desc "Create Admin user for Dspace "
    task :create_admin, :roles=> [:app] do
	[
	"echo #{dspace_admin_email} > #{dspace_home}/adm.txt",
	"echo #{dspace_admin_fname} >> #{dspace_home}/adm.txt",
	"echo #{dspace_admin_lname} >> #{dspace_home}/adm.txt",
	"echo #{dspace_admin_password} >> #{dspace_home}/adm.txt",
	"echo #{dspace_admin_password} >> #{dspace_home}/adm.txt",
	"echo y >> #{dspace_home}/adm.txt",
	"cd #{dspace_home}/bin && ./create-administrator < #{dspace_home}/adm.txt"
#	"cd #{dspace_maven_target_dir} && JAVA_HOME=#{java6_home} #{ant_home}/bin/ant fresh_install"
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant",
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant fresh_install"
	].each {|cmd| run cmd}	
    end
    
   
end
