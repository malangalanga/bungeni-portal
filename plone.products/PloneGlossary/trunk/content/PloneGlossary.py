# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: PloneGlossary.py 54798 2007-12-03 10:04:46Z glenfant $
"""
The Glossary content type
"""
__author__  = 'Cyrille Lebeaupin <clebeaupin@ingeniweb.com>'
__docformat__ = 'restructuredtext'


# Python imports

import string

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base
from zope.interface import implements
from zope.component import getMultiAdapter

# CMF imports
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils  import getToolByName

# Archetypes imports
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from Products.ATContentTypes.content.base import ATCTFolder

# Products imports
from Products.PloneGlossary.config import PROJECTNAME, PLONEGLOSSARY_CATALOG
from Products.PloneGlossary.PloneGlossaryCatalog import PloneGlossaryCatalog, manage_addPloneGlossaryCatalog
from Products.PloneGlossary.content.schemata import PloneGlossarySchema as schema
from Products.PloneGlossary.utils import encode, LOG
from Products.PloneGlossary.interfaces import IPloneGlossary

class PloneGlossary(ATCTFolder):
    """PloneGlossary container"""

    implements(IPloneGlossary)

    meta_type = 'PloneGlossary'
    definition_types = ('PloneGlossaryDefinition',)
    schema =  schema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'alphabetise')

    def alphabetise(self):
        items = self.getFolderContents({'sort_on':'sortable_title'})

        alphabets = {}
        for x in string.uppercase:
            alphabets[x] = []

        for item in items:
            char = item.Title[0].upper()
            if not alphabets.has_key(char):
                continue
            alphabets[char].append(item)

        return [{'letter': x, 'items': alphabets[x]} for x in \
            string.uppercase]
            
    def trunc(self,s,min_pos=0,max_pos=35,ellipsis=True):
        # Sentinel value -1 returned by String function rfind
        NOT_FOUND = -1
        # Error message for max smaller than min positional error
        ERR_MAXMIN = 'Minimum position cannot be greater than maximum position'
    
        # If the minimum position value is greater than max, throw an exception   
        if max_pos < min_pos:
            raise ValueError(ERR_MAXMIN)
        # Change the ellipsis characters here if you want a true ellipsis
        if ellipsis and len(s) > max_pos:
            suffix = '...'
        else:
            suffix = ''
        # Case 1: Return string if it is shorter (or equal to) than the limit
        length = len(s)
        if length <= max_pos:
            return s + suffix
        else:
            # Case 2: Return it to nearest period if possible
            try:
                end = s.rindex('.',min_pos,max_pos)
            except ValueError:
                # Case 3: Return string to nearest space
                end = s.rfind(' ',min_pos,max_pos)
                if end == NOT_FOUND:
                    end = max_pos
            return s[0:end] + suffix             

    def getGlossaryDefinitions(self, terms):
        """Returns glossary definitions.
        Returns tuple of dictionnary title, text.
        Definition is based on catalog getText metadata."""

        # Get glossary catalog
        title_request = ' OR '.join(['"%s"' % x for x in terms if len(x) > 0])
        if not title_request:
            return []

        # Get # Get glossary related term brains
        cat = self.getCatalog()
        brains = cat(Title=title_request)
        if not brains:
            return []

        # Build definitions
        definitions = []
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        mtool = plone_tools.membership()
        # mtool = getToolByName(self, 'portal_membership')
        for brain in brains:
            # Check view permission
            # FIXME: Maybe add allowed roles and user index in glossary catalog
            obj = brain.getObject()
            has_view_permission = mtool.checkPermission(CMFCorePermissions.View, obj) and mtool.checkPermission(CMFCorePermissions.AccessContentsInformation, obj)
            if not has_view_permission:
                continue

            # Make sure the title of glossary term is not empty
            title = brain.Title
            if not title:
                continue

            # Build definition
            item = {
                'id' : brain.id,
                'title' : brain.Title,
                'variants' : brain.getVariants,
                'description' : brain.Description,
                'url' : brain.getURL()}
            definitions.append(item)

        return tuple(definitions)

    security.declareProtected(CMFCorePermissions.View, 'getGlossaryTerms')
    def getGlossaryTerms(self):
        """Returns glossary terms title."""

        # Get glossary term titles
        return [x['title'] for x in self.getGlossaryTermItems()]

    # Make it private because this method doesn't check term security
    def _getGlossaryTermItems(self):
        """Returns glossary terms in a specific structure

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - description -> term description
        - url -> term url
        """

        # Returns all glossary term brains
        cat = self.getCatalog()
        brains = cat(REQUEST={})

        # Build items
        items = []
        for brain in brains:
            items.append({'path': brain.getPath(),
                          'id': brain.id,
                          'title': brain.Title,
                          'variants': brain.getVariants,
                          'description': brain.Description,
                          'url': brain.getURL(),})
        return items

    security.declarePublic('getGlossaryTermItems')
    def getGlossaryTermItems(self):
        """Returns the same list as _getGlossaryTermItems but check security."""

        # Get glossaries term items
        not_secured_term_items = self._getGlossaryTermItems()

        # Walk into each catalog of glossaries and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        # utool = getToolByName(self, 'portal_url')
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                obj = portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)
        return term_items

    security.declarePublic('getCatalog')
    def getCatalog(self):
        """Returns catalog of glossary"""

        if not hasattr(self, PLONEGLOSSARY_CATALOG):
            # Build catalog if it doesn't exist
            catalog = self._initCatalog()
        else :
            catalog = getattr(self, PLONEGLOSSARY_CATALOG)

        return catalog

    def _initCatalog(self):
        """Add Glossary catalog"""

        if not hasattr(self, PLONEGLOSSARY_CATALOG):
            add_catalog = manage_addPloneGlossaryCatalog
            add_catalog(self)

        catalog = getattr(self, PLONEGLOSSARY_CATALOG)
        catalog.manage_reindexIndex()
        return catalog


    security.declareProtected(CMFCorePermissions.ManagePortal, 'rebuildCatalog')
    def rebuildCatalog(self):
        """Delete old catalog of glossary and build a new one"""

        # Delete catalog if exists
        if hasattr(self, PLONEGLOSSARY_CATALOG):
            self.manage_delObjects([PLONEGLOSSARY_CATALOG])

        # Add a new one
        cat = self._initCatalog()

        # Reindex glossary definitions
        for obj in self.objectValues():
            if obj.portal_type in self.definition_types:
                cat.catalog_object(obj)

registerType(PloneGlossary, PROJECTNAME)

###
## Events handlers
###

def glossaryAdded(glossary, event):
    """A glossary has been added"""

    container = event.newParent
    # FIXME: Fix this when AT don't need manage_afterAdd any more
    super(glossary.__class__, glossary).manage_afterAdd(glossary, container)
    glossary._initCatalog()
    LOG.info("Event: A %s has been added.", glossary.meta_type)
    return

def glossaryMoved(glossary, event):
    """A glossary has been moved or renamed"""

    glossary.rebuildCatalog()
    LOG.info("Event: A %s has been moved.", glossary.meta_type)
    return

