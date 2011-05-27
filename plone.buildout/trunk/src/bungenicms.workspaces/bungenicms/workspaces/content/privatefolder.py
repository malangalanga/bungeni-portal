"""Definition of the Private Folder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bungenicms.workspaces.interfaces import IPrivateFolder
from bungenicms.workspaces.config import PROJECTNAME

PrivateFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PrivateFolderSchema['title'].storage = atapi.AnnotationStorage()
PrivateFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PrivateFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class PrivateFolder(folder.ATFolder):
    """A private folder for use by a principal. Content can only be in the private state."""
    implements(IPrivateFolder)

    meta_type = "PrivateFolder"
    schema = PrivateFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(PrivateFolder, PROJECTNAME)
