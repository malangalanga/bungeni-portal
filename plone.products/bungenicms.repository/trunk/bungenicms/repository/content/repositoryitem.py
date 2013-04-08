"""Definition of the Repository Item content type
"""

from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm # FOO

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.file import ATFile
from Products.ATVocabularyManager import NamedVocabulary
from collective.dynatree.atwidget import DynatreeWidget
from archetypes.multifile.MultiFileField import MultiFileField
from archetypes.multifile.MultiFileWidget import MultiFileWidget

try:
    from plone.app.blob.field import BlobField
except ImportError:
    #use default FileField
    BlobField = atapi.FileField

from bungenicms.repository import repositoryMessageFactory as _

from bungenicms.repository.interfaces import IRepositoryItem, IRepositoryItemBrowser
from bungenicms.repository.config import PROJECTNAME

GROUPS_VOCAB = u"bungenicms_repository_groups_vocab" 
YEARS_VOCAB = u"bungenicms_repository_years_vocab" 
MONTHS_VOCAB = u"bungenicms_repository_months_vocab" 
DAYS_VOCAB = u"bungenicms_repository_days_vocab" 


#RepositoryItemSchema = ATFile.schema.copy() + atapi.Schema((
RepositoryItemSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField('legislative_type',
        required = 1,
        vocabulary = NamedVocabulary('org.bungeni.metadata.vocabularies.parliamentarytypes'),
        widget = atapi.SelectionWidget(
            label = _('Type'),
            description = _('Choose the applicable document type'),
        ),
    ),
    atapi.LinesField('item_authors',
            required = 1,
            multiValued = True,
            searchable = True,
            widget = atapi.LinesWidget(
                label = _('Source'),
                description = _('List the authors/sponsors of this item.'),
                cols = 5,
                rows = 2,
            )
    ), 
    atapi.StringField('publication_number',
            required=False,
            searchable=True,
            widget=atapi.StringWidget(
                label=_(u"Number"),
                description=_(u"Publication Number"),
            )                
        ),        
    atapi.StringField('item_publisher',
        required = 0,
        vocabulary_factory = GROUPS_VOCAB,
        widget = atapi.SelectionWidget(
            label = _('Published By'),
            description = _('Choose a publisher'),
        ),
    ),
    atapi.StringField('item_publication_day',
        required=False,
        searchable = True,
        vocabulary_factory = DAYS_VOCAB,
        widget = atapi.SelectionWidget(
            label = _('Day'),
            description = _('Choose the publication day'),
        ),
    ),
    atapi.StringField('item_publication_month',
        required=False,
        searchable = True,
        vocabulary_factory = MONTHS_VOCAB,
        widget = atapi.SelectionWidget(
            label = _('Month'),
            description = _('Choose the publication month'),
        ),
    ), 
    atapi.StringField('item_publication_year',
        required=True,
        searchable = True,
        vocabulary_factory = YEARS_VOCAB,
        widget = atapi.SelectionWidget(
            label = _('Year'),
            description = _('Choose the publication year'),
        ),
    ),       
    atapi.LinesField('item_contributors',
            required = 0,
            multiValued = True,
            searchable = True,
            widget = atapi.LinesWidget(
                label = _('Contributors'),
                description = _('List the contributors to this item'),
                cols = 5,
                rows = 2,
            )    
    ),     
    MultiFileField('item_files',
               primary=True,
               languageIndependent=True,
               storage = atapi.AnnotationStorage(migrate=True),
               searchable = True,
               widget = MultiFileWidget(
                         description = "Select the file to be added by clicking the 'Browse' button.",
                         label= "Files",
                         show_content_type = True,
               )
    ),
    atapi.TextField('item_description',
        required = 0,
        searchable = True,
        default_content_type = "text/plain",
        default_output_type ="text/x-html-safe",
        widget = atapi.TextAreaWidget(
            label = _('Description'),
            description=_(u"A short description of this item"), 
            rows = 7
        )
    ),
    atapi.LinesField('subject_terms',
        required = 0,
        vocabulary = NamedVocabulary('org.bungeni.metadata.vocabularies.subjectterms'),
        widget = DynatreeWidget(
            label = _('Subject Terms'),
            description = _("Choose the applicable subject terms for this item"),
            selectMode = 2,
            autoCollapse = True,
            leafsOnly = False),
    ),    
    atapi.TextField('item_abstract',
        required = 0,
        searchable = True,
        default_content_type = "text/html",
        default_output_type ="text/x-html-safe",
        widget = atapi.RichWidget(
            label = _('Abstract'),
            rows = 20,
            allow_file_upload = True
        )
    ),   

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

#RepositoryItemSchema['title'].storage = atapi.AnnotationStorage()
#RepositoryItemSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(RepositoryItemSchema, moveDiscussion=False)

 #hide the description - we use abstract
RepositoryItemSchema['description'].widget.visible = {"edit": "invisible",
                                                      "view": "invisible"}

class RepositoryItem(base.ATCTContent):
    """Repository Item"""
    implements(IRepositoryItem)

    meta_type = "RepositoryItem"
    schema = RepositoryItemSchema

 
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(RepositoryItem, PROJECTNAME)
