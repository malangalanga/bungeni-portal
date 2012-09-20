from Products.FacultyStaffDirectory.interfaces.facultystaffdirectory import IFacultyStaffDirectory
from archetypes.schemaextender.interfaces import ISchemaModifier, IBrowserLayerAwareExtender
from bungeni.FacultyStaffExtender.interfaces import IFacultyStaffExtenderLayer
from zope.component import adapts
from zope.interface import implements

class FacultyStaffDirectoryExtender(object):
    """
    Adapter to add description field to a FacultyStaffDirectory.
    """
    adapts(IFacultyStaffDirectory)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)

    layer = IFacultyStaffExtenderLayer
    
    fields = [
    ]    

    def __init__(self, context):
        self.context = context
        
    def getFields(self):
        return self.fields

    def fiddle(self, schema):
        desc_field = schema['description'].copy()
        desc_field.schemata = "default"
        schema['description'] = desc_field
