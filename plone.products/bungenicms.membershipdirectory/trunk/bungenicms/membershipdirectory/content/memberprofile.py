"""Definition of a Member Profile content type
"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import View

from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

from bungenicms.membershipdirectory.interfaces import IMemberProfile
from bungenicms.membershipdirectory.config import PROJECTNAME

from bungenicms.membershipdirectory.vocabularies import COUNTY_LIST
from bungenicms.membershipdirectory.vocabularies import CONSTITUENCIES_LIST

ELECTED_LIST = atapi.DisplayList((
    ('elected', 'Elected'), 
    ('nominated', 'Nominated'),
    ))
    
STATUS_LIST = atapi.DisplayList((
    ('current', 'Current'), 
    ('former', 'former'),
    ))
    
constituency = ({'name': 'constituency', 
          'action': 'vocabulary', 
          'vocab_method': 'getConstituencyVocab', 
          'control_param': 'master', 
         }, )     
    

MemberProfileSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField('other_names',
        required = 1,
        widget = atapi.StringWidget(
            label=u"Other Names",
            description=u"Other Names",
        ),
    ),
    atapi.StringField('member_role',
        required = 0,
        widget = atapi.StringWidget(
            label=u"Role",
            description=u"Role of member",
        ),
    ),
    atapi.StringField('political_party',
        required = 1,
        widget = atapi.StringWidget(
            label=u"Political Party",
            description=u"Political Party of member",
        ),
    ),
    atapi.StringField('county', 
        required=0, 
        searchable=1, 
        vocabulary=COUNTY_LIST, 
        widget = MasterSelectWidget(
            slave_fields = constituency,
            label = u"County",
            description=u"Member County",
        ),
     ), 
                        
     atapi.StringField('constituency',
        required = 0,
        searchable=1, 
        default = '',
        widget = atapi.SelectionWidget(
            format='select',
            label=u"Constituency",
            description=u"Member Constituency",
        ),
     ),
    atapi.StringField('elected_nominated',
        required = True,
        default = 'elected',
        vocabulary = ELECTED_LIST,
        widget = atapi.SelectionWidget(
            label = u"Elected / Nominated",
            description = u"Is the member Elected or Nominated?",
            type = 'radio',
        ),
    ),
    atapi.StringField('member_status',
        required = True,
        default = 'current',
        vocabulary = STATUS_LIST,
        widget = atapi.SelectionWidget(
            label = u"Current / Former",
            description = u"Is this a current member or a former member?",
            type = 'radio',
        ),
    ),
    atapi.ImageField('member_image',
        widget = atapi.ImageWidget(
            label = u"Member Image",
            description = u"Photo of the member",
        ),
        sizes = {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
    ),
    atapi.TextField('body_text',
        required = 0,
        searchable = True,
        default_content_type = "text/html",
        default_output_type ="text/x-html-safe",
        widget = atapi.RichWidget(
            label = u'Body Text',
            rows = 20,
            allow_file_upload = True
        )
    ),    
    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

MemberProfileSchema['title'].storage = atapi.AnnotationStorage()
MemberProfileSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(MemberProfileSchema, moveDiscussion=False)

MemberProfileSchema['title'].widget.label = u'Surname'
MemberProfileSchema.moveField('description', before='body_text')

class MemberProfile(base.ATCTContent):
    """Member Profile"""
    implements(IMemberProfile)

    meta_type = "MemberProfile"
    schema = MemberProfileSchema
    
    security = ClassSecurityInfo()
    
    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = 'Member image'
        return self.getField('member_image').tag(self, **kwargs)
        
    
    security.declarePublic('getConstituencyVocab')
    def getConstituencyVocab(self, master):
        """Vocab method that returns a vocabulary consisting of the 
        constituencies from the given county.
        """
        results = CONSTITUENCIES_LIST[master]
        results = [(item, item) for item in results] 
        return atapi.DisplayList(results)
 
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MemberProfile, PROJECTNAME)
