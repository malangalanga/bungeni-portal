'''
Created on May 20, 2011

@author: Ashok
'''
"""
XML Document classes
"""

from org.dom4j.io import SAXReader
from org.dom4j.io import XMLWriter
from org.dom4j.io import OutputFormat

from java.io import File
from java.io import FileWriter

class XML:
    
    __sax_parser_factory__ = "org.apache.xerces.jaxp.SAXParserFactoryImpl"
    
    def __init__(self, xml_path):
        self.xmlfile = xml_path
        self.xmldoc = None
        self.__load_xml__()
    
    def __load_xml__(self):
        xml_file = File(self.xmlfile)
        sr = SAXReader()
        self.xmldoc =  sr.read(xml_file)
    
    def reload(self):
        """
        Reloads the XML document 
        """
        self.__load_xml__()
    
    def backup_xml(self, file):
        """
        Makes a backup copy of the xml document, 
        file is suffixed with iso datetime
        """
        from time import strftime
        fsuffix = strftime("%Y%m%d-%H%M%S")
        backup_file = file + fsuffix
        from shutil import copyfile
        copyfile(file, backup_file)
            
    def save_xml(self, path , pretty = True):
        """
        Saves the xml document to file
        """
        self.backup_xml(path)
        
        format = None
        xmlwriter = None
        
        if pretty == True:
            format = OutputFormat.createPrettyPrint()
            format.setIndent("    ")
            format.setLineSeparator("\r\n")
        
        if format is None:
            xmlwriter = XMLWriter(FileWriter(path))
        else:
            xmlwriter = XMLWriter(FileWriter(path), format)
            
        xmlwriter.write(self.xmldoc)
        xmlwriter.close()


class UIXML(XML):
    """
    Loads ui.xml into dom and provides xml api access to it
    """
    __descriptor_path__ = "//ui/descriptor"

    def __init__(self, xml_path = "/home/undesa/cinst/bungeni/src/bungeni_custom/forms/ui.xml"):
        XML.__init__(self, xml_path)

    def save_xml(self):
        """
        Simply call the parent class save_xml
        """
        XML.save_xml(self, self.xmlfile, True)


    def get_roles(self):
        """
        Returns a list of roles in ui[@roles]
        """
        roles = self.xmldoc.getRootElement().attributeValue("roles")
        return roles.split(" ")
    
    def get_form_names(self):
        """
        Returns all the <descriptor> tags
        """
        form_names = []
        nodes = self.xmldoc.selectNodes(self.__descriptor_path__)
        for element in nodes:
            attrs = element.attributes()
            for attr in attrs:
                form_names.append( attr.getValue())
        return form_names

    def xpath_form_by_name(self,form_name):
        return self.__descriptor_path__ + "[@name='" + form_name + "']"
                    
    def xpath_form_fields(self, form_name):
        return self.xpath_form_by_name(form_name) + "//field"
    
    def xpath_form_field(self, form_name, field_name):
        return  self.xpath_form_by_name(form_name)+ "/field[@name='"+field_name+"']"
    
    def xpath_form_field_show(self, form_name, field_name):
        return self.xpath_form_field(form_name, field_name)+"/show"

    def xpath_form_field_hide(self, form_name, field_name):
        return self.xpath_form_field(form_name, field_name)+"/hide"
        
    def get_form_by_name(self,form_name):
        """
        get descriptor node
        """
        nodes = self.xmldoc.selectSingleNode(self.xpath_form_by_name(form_name))
        return nodes
    
    def get_form_fields(self, form_name):
        """
        get all fields in descriptor
        """
        nodes = self.xmldoc.selectNodes(self.xpath_form_fields(form_name))
        return nodes
   
    def get_form_field(self, form_name, field_name):
        """
        Returns a specific <field> from a <descriptor>
        """
        return self.xmldoc.selectSingleNode(self.xpath_form_field(form_name, field_name))

    def get_form_field_show(self, form_name, field_name):
        """
        Returns a <show> element in a specific <field> in a <descriptor>
        """
        return self.xmldoc.selectSingleNode( self.xpath_form_field_show(form_name, field_name))

    def get_form_field_hide(self, form_name, field_name):
        """
        Returns a <hide> element in a specific <field> in a <descriptor>
        """
        return self.xmldoc.selectSingleNode(self.xpath_form_field_hide(form_name, field_name))


class WorkflowXML(XML):
    
    __workflow_root__ = "/workflow"
    

    def xpath_workflow(self):
        return self.__workflow_root__
    

    def xpath_workflow_states(self):
        return self.xpath_workflow() + "/state"
    

    def xpath_workflow_state(self, id):
        return self.xpath_workflow_states() + "[@id='"+  id + "']"
    

    def xpath_relative_state_assignments(self):
        return str("/*[name() = 'grant' or name() = 'deny']")
    

    def xpath_workflow_state_assignments(self, id):
        return self.xpath_workflow_state(id) + self.xpath_relative_state_assignments()
    

    def get_workflow(self):
        return self.xmldoc.selectSingleNode(self.__workflow_root__)
    

    def get_title(self):
        return self.get_workflow().attributeValue("title")
            

    def get_states(self):
        return self.xmldoc.selectNodes(self.xpath_workflow_states())
    

    def get_state(self, id):
        return self.xmldoc.selectSingleNode(self.xpath_workflow_state(id))
    

    def __get_inherited_assignments(self, id, key, assignments, order):
        state = self.get_state(id)
        state_assignment = self.StateAssignment(key, 
                                                order, 
                                                self.xmldoc.selectNodes(
                                                    self.xpath_workflow_state_assignments(id)
                                                    )
                                                )
        assignments.append(state_assignment)
        like_state = state.attributeValue("like_state")
        if like_state is not None:
            return self.__get_inherited_assignments(like_state, 
                                                    like_state, 
                                                    assignments, 
                                                    order + 1)
        else:
            return assignments    
    

    def get_state_assignments(self, id):
        """
        Gets all grants, including, ones inherited from like_state.
        Permissions are grouped by inherited state. The state represented
        by id is identified by the 'self' name
        Returns a list of StateAssignment objects
        """
        assignments=[]
        order = 0
        assignments = self.__get_inherited_assignments(id, "self", 
                                                       assignments, 
                                                       order)
        return assignments


    def get_applicable_state_assignments(self, id):
        """
        Returns a list of applicable grants for an object,
        inherited grants are normalized, i.e. only the last applicable 
        grant / deny is reflected as 'active'
        """
        inherited_assignments = self.get_state_assignments(id)
        inherited_assignments = sorted(inherited_assignments, key=lambda state_assignment: state_assignment.order, reverse=True)
        permission_assignments = []
        for state_grants in inherited_assignments:
            print "state_grants == " , state_grants
            for state_grant in state_grants.assignments:
                
                key = state_grants.key
                grant_or_deny = state_grant.getQName().getName()
                permission = state_grant.attributeValue("permission")
                role = state_grant.attributeValue("role")
                grant_boolean =  True if grant_or_deny=="grant" else False
                inherited_boolean = False if key == "self" else True
                
                p_g = self.PermissionGrant(permission = permission, 
                                           role = role, 
                                           grant= grant_boolean, 
                                           inherited = inherited_boolean)
                
                if  p_g not in permission_assignments:
                    permission_assignments.append(p_g)
                else:
                    p_g = permission_assignments[permission_assignments.index(p_g)]
                    p_g.grant = grant_boolean
                    p_g.inherited = inherited_boolean
                                                  
        return permission_assignments

    class StateAssignment:
        """
        Used by get_state_assignments
        """
        
        def __init__(self, key, order, assignments):
            self.key = key
            self.order = order
            self.assignments = assignments
        
        def __str__(self):
            return "key="+self.key + ", order=" + str(self.order) + ", assign=" + str(self.assignments)
    
        def __repr__(self):
            return self.__str__()
    

    class PermissionGrant:
        """
        Used by get_applicable_state_assignments
        """
            
        def __init__(self, permission="zope.View", grant=True, 
                     role="bungeni.Anonymous", inherited = True):
            """
            The permission associated with the grant
            """
            self.permission = permission
            """
            The role associated with the grant
            """
            self.role = role
            """
            boolean - grant = True, deny = False
            """
            self.grant = grant
            """
            Is the grant inherited ? if the grant is declaredin a like_state 
            and not in the state in the current context,then inherited = True, 
            otherwise if it is declared locally in the state inherited = False
            """
            self.inherited = inherited
            
        def __cmp__(self, other):
            """
            Override the default behavior of __cmp__ since we want to compare
            the object only on permission and role.
            If the permission and role match between 2 objects, we declare them 
            equal. This allows us to retrieve matching PermissionGrant objects
            """
            if cmp(self.permission, other.permission) == 0 and cmp(self.role, other.role) == 0:
                return 0
            else:
                return -1
             
 
        def __repr__(self):
            return (
                    ("grant" if self.grant else "deny") + " " +  
                    self.permission + "," + self.role + " "
                    ("*inherited*" if self.inherited else "*local*")
                   )
                

 
class _RolesXML(XML):
    """
    Query class to get roles from roles.zcml
    """
     
    __roles_root__ = "/configure"
    
    def xpath_roles(self):
        return self.__roles_root__+ "/role"
        
    def get_roles(self):
        return self.xmldoc.selectNodes(self.xpath_roles())

class Role:
    
    def __init__(self, role_node):
        self.id = role_node.attributeValue("id")
        self.title =role_node.attributeValue("title")
    
    def __repr__(self):
        return self.id


class Roles:

    def __init__(self, roles_files):
        self.roles = []
        for roles_file in roles_files:
            rolesxml = _RolesXML(roles_file)
            for role in rolesxml.get_roles():
                self.roles.append(Role(role))
        
    
