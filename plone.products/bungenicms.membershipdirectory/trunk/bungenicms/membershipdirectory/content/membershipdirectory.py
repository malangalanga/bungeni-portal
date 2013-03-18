"""Definition of the Membership Directory content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from bungenicms.membershipdirectory import membershipdirectoryMessageFactory as _

from bungenicms.membershipdirectory.interfaces import IMembershipDirectory, IMemberProfileBrowser
from bungenicms.membershipdirectory.config import PROJECTNAME

MembershipDirectorySchema = folder.ATFolderSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MembershipDirectorySchema['title'].storage = atapi.AnnotationStorage()
MembershipDirectorySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    MembershipDirectorySchema,
    folderish=True,
    moveDiscussion=False
)

class MembershipDirectory(folder.ATFolder):
    """Membership Directory"""
    implements(IMembershipDirectory, IMemberProfileBrowser)

    meta_type = "MembershipDirectory"
    schema = MembershipDirectorySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MembershipDirectory, PROJECTNAME)
