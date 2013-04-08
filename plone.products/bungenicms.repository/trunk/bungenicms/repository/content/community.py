"""Definition of the Community content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import folder

# -*- Message Factory Imported Here -*-

from bungenicms.repository.interfaces import ICommunity
from bungenicms.repository.config import PROJECTNAME

CommunitySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

CommunitySchema['title'].storage = atapi.AnnotationStorage()
CommunitySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(CommunitySchema, 
							folderish = True,
							moveDiscussion=False)


class Community(base.ATCTContent):
    """Repository Community"""
    implements(ICommunity)

    meta_type = "Community"
    schema = CommunitySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Community, PROJECTNAME)
