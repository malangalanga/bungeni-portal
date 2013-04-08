"""Definition of the Repository Collection content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from Products.ATVocabularyManager import NamedVocabulary

# -*- Message Factory Imported Here -*-
from bungenicms.repository import repositoryMessageFactory as _

from bungenicms.repository.interfaces import IRepositoryCollection, IRepositoryItemBrowser
from bungenicms.repository.config import PROJECTNAME

from Products.ATVocabularyManager import NamedVocabulary
from collective.dynatree.atwidget import DynatreeWidget

RepositoryCollectionSchema = folder.ATFolderSchema.copy() + atapi.Schema((

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

RepositoryCollectionSchema['title'].storage = atapi.AnnotationStorage()
RepositoryCollectionSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    RepositoryCollectionSchema,
    folderish=True,
    moveDiscussion=False
)


class RepositoryCollection(folder.ATFolder):
    """Repository Collection"""
    implements(IRepositoryCollection, IRepositoryItemBrowser)

    meta_type = "RepositoryCollection"
    schema = RepositoryCollectionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(RepositoryCollection, PROJECTNAME)
