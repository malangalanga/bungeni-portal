# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('BungeniHelpCenter')
logger.info('Installing Product')

import os, os.path
from Globals import package_home
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import DirectoryView
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize
from config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/bungeni_help_center',
                                    product_globals)

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
import monkeypatch

def initialize(context):
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import content
    import interfaces

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    profile_registry.registerProfile('bungenihelpcenter',
                                     'BungeniHelpCenter',
                                     'BungeniHelpCenter',
                                     'profiles/default',
                                     'BungeniHelpCenter',
                                     EXTENSION,
                                     for_=IPloneSiteRoot)


    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom

