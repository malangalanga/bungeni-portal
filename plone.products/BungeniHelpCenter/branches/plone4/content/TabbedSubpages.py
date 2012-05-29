from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.CMFCore.permissions import View
from Products.PloneHelpCenter.config import REFERENCEABLE_TYPES, IMAGE_SIZES, PROJECTNAME

from Products.BungeniHelpCenter.config import TYPE_PARAMS
from Products.BungeniHelpCenter.config import BUNGENI_REFERENCEABLE_TYPES

from time import sleep
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *
try:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
    PHCReferenceWidget = ReferenceBrowserWidget
except ImportError:
    PHCReferenceWidget = ReferenceWidget
try:
    from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault
    HAS_ISBD = True
except ImportError:
    HAS_ISBD = False

RelatedItemsField =  ReferenceField(
        'relatedItems',
        relationship='PloneHelpCenter',
        allowed_types=BUNGENI_REFERENCEABLE_TYPES,
        required = 0,
        multiValued=1,
        languageIndependent=1,
        widget=PHCReferenceWidget (
                label="Referenced Items",
                description="Set one or more references to HelpCenter items.",
                description_msgid = "phc_reference",
                label_msgid = "phc_label_reference",
                i18n_domain="plonehelpcenter"
                ),
    )

TabbedSubpagesSchema = ATDocumentSchema.copy() + Schema((RelatedItemsField),)

TabbedSubpagesSchema['title'].required = 0
TabbedSubpagesSchema['text'].required = 0

class TabbedSubpages(ATDocument):
    """
    Represents a page aggregating the content of referenced "sub-pages".
    Each sub-page gets a tab so that only one sub-page is shown at a time.
    """
    
    security = ClassSecurityInfo()
    global_allow = 1
    portal_type = meta_type = TYPE_PARAMS['TabbedSubpages']['portal_type']
    archetype_name = TYPE_PARAMS['TabbedSubpages']['archetype_name']
    immediate_view = default_view = TYPE_PARAMS['TabbedSubpages']['default_view']
    
    actions = ({ 'id': 'view'
             , 'name': 'View'
             , 'action': 'string:${object_url}/' + default_view
             , 'permissions': (View,)
             },
            )
    
    schema = TabbedSubpagesSchema
    
    security.declareProtected(View, 'getTargetObjectLayout')
    def getTargetObjectLayout(self, target):
        """
        Returns target object 'view' action page template
        """
        
        if HAS_ISBD and ISelectableBrowserDefault.providedBy(target):
            return target.getLayout()
        else:
            view = target.getTypeInfo().getActionById('view') or 'base_view'
            
            # If view action is view, try to guess correct template
            if view == 'view':
                view = target.portal_type.lower() + '_view'
                
            return view
            

try:
  from Products.LinguaPlone.public import registerType
except ImportError:
  from Products.Archetypes.public import registerType
  
registerType(TabbedSubpages, PROJECTNAME)
