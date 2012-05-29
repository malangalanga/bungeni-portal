from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.CMFCore.permissions import View
from Products.PloneHelpCenter.config import REFERENCEABLE_TYPES, IMAGE_SIZES, PROJECTNAME

from Products.BungeniHelpCenter.config import TYPE_PARAMS
from Products.BungeniHelpCenter.config import BUNGENI_REFERENCEABLE_TYPES

from Products.PloneHelpCenter.config import *
from Products.PloneHelpCenter.content.schemata import HelpCenterBaseSchema
from Products.PloneHelpCenter.content.PHCContent import PHCContent
from Products.PloneHelpCenter.content.ReferenceManualPage import HelpCenterReferenceManualPage
from Products.PloneHelpCenter.content import ReferenceManual,\
    Tutorial, TutorialPage, ReferenceManualPage, ReferenceManualSection
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin, fti_meta_type



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

try:
    import Products.CMFCore.permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions



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

#CompositePageSchema = HelpCenterBaseSchema.copy() + Schema((RelatedItemsField),)


HelpCenterReferenceManualPage = ReferenceManualPage.HelpCenterReferenceManualPage

HelpCenterReferenceManualPage.schema['description'].required = 0


#CompositePageSchema['title'].required = 0
#CompositePageSchema['text'].required = 0

CompositePageSchema =  HelpCenterReferenceManualPage.schema + Schema((RelatedItemsField),)

class CompositePage(BrowserDefaultMixin, OrderedBaseFolder, HelpCenterReferenceManualPage):
    """Represents a page that can contain Tabbed Pages. """
    __implements__ = (PHCContent.__implements__)

    
    security = ClassSecurityInfo()
    schema = CompositePageSchema
    global_allow = 1    
    portal_type = meta_type = 'CompositePage'
    archetype_name = 'CompositePage'
    filter_content_types = 1
    allowed_content_types = ('TabbedSubpages',)
    default_view = 'compositepage_view'
    suppl_views = ('compositepage_horizontal_tabs', 'compositepage_vertical_tabs',)

    security = ClassSecurityInfo()

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

    def SearchableText(self):
        """Append references' searchable fields."""
        
        data = [HelpCenterReferenceManualPage.SearchableText(self),]
        
        subpages = self.objectValues(['TabbedSubpages',])
        for subpage in subpages:
            data.append(subpage.SearchableText())
            
        data = ' '.join(data)
        
        return data

    
    actions = (
             {'id': 'view'
             , 'name': 'View'
             , 'action': 'string:${object_url}/' + default_view
             , 'permissions': (View,)
             },
             {'id'          : 'edit',
               'name'        : 'Edit',
               'action'      : 'string:${object_url}/edit',
               'permissions' : (CMFCorePermissions.ModifyPortalContent,),
             },
             {'id'          : 'metadata',
              'name'        : 'Properties',
              'action'      : 'string:${object_url}/properties',
              'permissions' : (CMFCorePermissions.ModifyPortalContent,),
             },
             {'id'          : 'local_roles',
              'name'        : 'Sharing',
              'action'      : 'string:${object_url}/sharing',
              'permissions' : (CMFCorePermissions.ManageProperties,),
             },
            )

    aliases = {
        '(Default)'  : '(dynamic view)',
        'view'       : '(selected layout)',
        'index.html' : '',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form',
        'stats'      : 'phc_stats',
        'gethtml'    : '',
        'mkdir'      : '',
        }
    

    
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
            
  
registerType(CompositePage, PROJECTNAME)
