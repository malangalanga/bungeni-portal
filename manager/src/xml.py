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


        