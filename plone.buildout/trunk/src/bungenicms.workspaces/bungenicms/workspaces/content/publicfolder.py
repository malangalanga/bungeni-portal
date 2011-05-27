"""Definition of the Public Folder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bungenicms.workspaces.interfaces import IPublicFolder
from bungenicms.workspaces.config import PROJECTNAME

PublicFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PublicFolderSchema['title'].storage = atapi.AnnotationStorage()
PublicFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PublicFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class PublicFolder(folder.ATFolder):
    """A public folder for use by a principal. Content can be published, private or pending review."""
    implements(IPublicFolder)

    meta_type = "PublicFolder"
    schema = PublicFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(PublicFolder, PROJECTNAME)
