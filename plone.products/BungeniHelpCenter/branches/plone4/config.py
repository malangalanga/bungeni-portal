# -*- coding: utf-8 -*-
# Dependend products - not quick-installed - used in testcase
# override in custom configuration
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
PROJECTNAME = "BungeniHelpCenter"
product_globals = globals()
DEPENDENCIES = ['PloneHelpCenter', 'AddRemoveWidget']

TYPE_PARAMS = {}
TYPE_PARAMS['TabbedSubpages'] = { 'portal_type' : 'TabbedSubpages'
                                , 'archetype_name' : 'Tabbed Subpages'
                                , 'default_view' : 'tabbed_subpages_view'
                                }

BUNGENI_REFERENCEABLE_TYPES = (
    'BungeniHelpCenterReferenceManual',
    'BungeniHelpCenterReferenceSection',
    'BungeniHelpCenterReferenceManualPage',
    'HelpCenterReferenceManual',
    'HelpCenterReferenceManualFolder',
    'HelpCenterReferenceManualSection',
    'HelpCenterReferenceManualPage',
    'HelpCenter',
    'HelpCenterTutorialFolder',
    'BungeniHelpCenterTutorial',
    'BungeniHelpCenterTutorialPage',
    'HelpCenterTutorial',
    'HelpCenterTutorialPage'
    'Document',
    'Event',
    'File',
    'Folder',
    'Image',
    'News Item',
    'Large Plone Folder',
    'TabbedSubpages',
    'Topic',
    'HelpCenter',
    'HelpCenterErrorReferenceFolder',    
    'HelpCenterErrorReference',    
    'HelpCenterFAQ',
    'HelpCenterFAQFolder',
    'HelpCenterGlossary',
    'HelpCenterDefinition',
    'HelpCenterHowTo',
    'HelpCenterHowToFolder',
    'HelpCenterLink',
    'HelpCenterLinkFolder',
    'CompositePage',
    'TabbedSubpages',    
    

)
