# -*- coding: utf-8 -*-
#
# File: Annotations.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Jordaan <jean.jordaan@gmail.com>"""
__docformat__ = 'plaintext'

import sys

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Marginalia.config import *
from Products.Marginalia.tools.SequenceRange import SequenceRange, SequencePoint
from Products.Marginalia.tools.XPathRange import XPathRange, XPathPoint
from Products.Marginalia.tools.RangeInfo import RangeInfo, mergeRangeInfos

from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
from cgi import parse_qsl
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema = Schema((

    LinesField(
        name='keywords',
        default=('Agree:This is a good point', 'Disagree:I think this is wrong', 'More Info:I need more information on this',),
        widget=LinesField._properties['widget'](
            label='Keywords',
            label_msgid='Marginalia_label_keywords',
            i18n_domain='Marginalia',
        )
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Annotations_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Annotations(UniqueObject, BaseBTreeFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(BaseBTreeFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Annotations'

    meta_type = 'Annotations'
    portal_type = 'Annotations'
    allowed_content_types = ['Annotation']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'Annotations.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Annotations"
    typeDescMsgId = 'description_edit_annotations'
    #toolicon = 'Annotations.gif'


    actions =  (


       {'action': "string:${object_url}/listAnnotations",
        'category': "object",
        'id': 'listAnnotations',
        'name': 'listAnnotations',
        'permissions': ("View",),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = Annotations_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseBTreeFolder.__init__(self,'portal_annotations')
        self.setTitle('Annotations')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
        
        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods

    security.declarePublic('preference')
    def preference(self):
        """ Quick & REST dirty preferences. Move to configlet later.
        """
        rest_verb_map = {
            'GET': self._listPreferences,
            'POST': self._setPreference,
            }
        verb = rest_verb_map[self.REQUEST.REQUEST_METHOD]
        return verb()

    security.declarePublic('annotate')
    def annotate(self, REQUEST=None):
        """ Examine request for REST verbs.
        """
        self.REQUEST['filter_type'] = 'annotate'
        rest_verb_map = {
            'GET': self._listAnnotations, # Finds listAnnotations.pt in skins
            'POST': self._createAnnotation,
            'PUT': self._updateAnnotation,
            'DELETE': self._deleteAnnotation,
            }
        verb = rest_verb_map[self.REQUEST.REQUEST_METHOD]
        return verb()

    security.declarePublic('amendment')
    def amendment(self, REQUEST=None):
        """ Examine request for REST verbs.
        """
        # Manipulating the request to avoid a lot of duplicate code
        if not self.REQUEST.has_key('filter_type'):
            self.REQUEST['filter_type'] = 'comment;insert;replace;delete'
        elif 'select_all' in self.REQUEST['filter_type']:
            self.REQUEST['filter_type'] = 'comment;insert;replace;delete'
        elif 'annotate' in self.REQUEST['filter_type']:
            raise Exception, "Annotations are not displayed in the amendment view"
        
        rest_verb_map = {
            'GET': self._listAnnotations, # Finds listAnnotations.pt in skins
            'POST': self._createAnnotation,
            'PUT': self._updateAnnotation,
            'DELETE': self._deleteAnnotation,
            }
        verb = rest_verb_map[self.REQUEST.REQUEST_METHOD]
        return verb()

    security.declarePublic('listKeywords')
    def listKeywords(self):
        """ Turn Python list into a list of lines
        """
        return '\n'.join(self.Schema()['keywords'].get(self))

    def isAdmin(self, context):
        """Returns true if the registered user is an administrator."""
        member  = self.portal_membership.getAuthenticatedMember()
        if member and "Reviewer" in member.getRolesInContext(context):
            return True
        return False

    def _getUser(self):
        """Returns User"""
        return self.portal_membership.getAuthenticatedMember()

    def _getUserName(self):
        """Returns User Name"""        
        return self._getUser().getUserName()

    security.declarePublic( 'getAnnotatedUrl' )
    def getAnnotatedUrl( self, url ):
        x = url.find( '/annotate' )
        if -1 != x:
            url = url[ : x ]
        return url

    security.declarePublic('getOwnerList')
    def getOwnerList(self, REQUEST=None):
        """Returns the list of owner names."""
        user = self._getUserName()
        url = self.getAnnotatedUrl(REQUEST.getURL())
        url = url.split("/@@")[0]
        annotations = self.getSortedFeedEntries(user, url)
        return set([annotation.Creator() for annotation in annotations])

    security.declarePublic('getOwnerList')
    def getPortalGroups(self, REQUEST=None):
        """Returns the list of portal wide groups."""
        groups = []
        for group in self.acl_users.getGroups():
            groups.append((group.id, group.getGroupName()))
        return groups

    security.declarePublic('getSortedFeedEntries')
    def getSortedFeedEntries(self, user, url, block=None, filter_name=None,\
                             filter_group=None, filter_type=None, search_string=None):
        """ The incoming query specifies an URL like 
        http://server/somedocument/annotate/#*
        where the fragment identifier ('#*') specifies all annotations
        for this page. The document is cataloged under the URL w/o
        fragment, so chop that to get the same effect. 

        To query per fragment identifier, filter the returned
        annotations by looking at their 'url' field.
        """
        catalog = getToolByName(self, 'portal_catalog')
			
        query = {
            'portal_type': 'Annotation',
            'getIndexed_url': url
            }
        if search_string:
            query['SearchableText'] = search_string

        public_annotations = catalog(query)
                    
        if user:
            query['Creator'] = user
            
        ps = catalog(query) + public_annotations

        # Filter by position (if block was specified )
        annotations = [ ]
        uids = []
        if block is not None and block != '':
            block = SequencePoint( block );
            for p in ps:
                annotation = p.getObject( )
                
                if annotation.UID() in uids:
                    continue
                uids.append(annotation.UID())
                
                arange = annotation.getSequenceRange( )
                if arange.start.compareInclusive( block ) <= 0 and arange.end.compareInclusive( block ) >= 0:
                    annotations.append( annotation )
        else:
            for p in ps:
                annotation = p.getObject( )
                if annotation.UID() in uids:
                    continue
                uids.append(annotation.UID())                
                annotations.append(annotation)

        if filter_name and "select_all" in filter_name:
            filter_name = None
        if filter_type and "select_all" in filter_type:
            filter_type = None
        if filter_group and "select_all" in filter_group:
            filter_group = None

        if filter_name:
            filter_name = filter_name.split(";")
            annotations = [annotation for annotation in annotations if annotation.Creator() in filter_name]

        if filter_type:
            filter_type = filter_type.split(";")
            annotations = [annotation for annotation in annotations if annotation.getEditType() in filter_type]

        if filter_group:
            filter_group = set(filter_group.split(";"))
            group_annotations = []
            for annotation in annotations:
                member = self.acl_users.getUserById(annotation.Creator())
                if not member:
                    continue
                if not set(member.getGroupIds()).intersection(filter_group):
                    continue
                group_annotations.append(annotation)
            annotations = group_annotations
            
        auth_member = self._getUser()        
        
        return  [annotation for annotation in annotations if auth_member.has_permission("View", annotation)]

    security.declarePublic('getRangeInfos')
    def getRangeInfos(self, user, url, filter_type=None):
        """ As with getSortedFeedEntries, but instead of returning individual
        annotations, return BlockInfo entries. """
        annotations = self.getSortedFeedEntries(user, url, filter_type = filter_type)
        infos = [ ]
        for annotation in annotations:
            info = RangeInfo( )
            info.fromAnnotation( annotation )
            infos.append( info )
        return mergeRangeInfos( infos )
    
    security.declarePublic('getFeedUID')
    def getFeedUID(self):
        """ The feed UID needs to be constant
        """
        return 'tag:%s:annotation' % self.UID()

    security.declarePublic('getBaseURL')
    def getBaseURL(self):
        """
        """
        return self.absolute_url()

    security.declarePrivate('_listPreferences')
    def _listPreferences(self):
        """ Stub .. TODO
        """
        return ('annotations.show:true\n' 'annotations.show-user:anonymous\n' 'annotations.note-edit-mode:note freeform\n')

    security.declarePrivate('_setPreference')
    def _setPreference(self):
        """
        """
        # TODO: Ignore prefence saving for now
        self.REQUEST.RESPONSE.setStatus('NoContent')
        return

    security.declarePrivate('_listAnnotations')
    def _listAnnotations(self):
        params = { 'format' : 'atom' }
        params.update( parse_qsl( self.REQUEST.QUERY_STRING ) )
        format = params[ 'format' ]
        if 'atom' == format:
            return self.listAnnotations( )
        elif 'blocks' == format:
            return self.listBlocks( )
        
    security.declarePrivate('_createAnnotation')
    def _createAnnotation(self):
        """ Create annotation from POST.
        """
        # TODO: do something useful with 'access'. Plone already
        # enforces security based on ownership, so access is 'private'
        # by default. 'public' access could mean sharing the annotation
        # with the 'Anonymous' role, though a more restrictive
        # implementation such as 'Member' or 'MemberOfParliament'
        # probably makes more sense.
        params = {
            'url': '',
            'block-range': '',
            'xpath-range': '',
            'note': '',
            'access': '',
            'status': '',                        
            'action': '',
            'quote': '',
            'quote_title': '',
            'quote_author': '',
            'link': '',
            }
        # TODO: Don't treat query string and body parameters as equivalent.
        # Query string parameters should identify the resources, while
        # parameters in the body should specify the action to take.
        params.update(self.REQUEST)
        params.update(parse_qsl(self.REQUEST.QUERY_STRING))
        sequenceRange = SequenceRange( params[ 'sequence-range' ] )
        xpathRange = XPathRange( params[ 'xpath-range' ] )

        params[ 'start_block' ] = sequenceRange.start.getPaddedPathStr( )
        params[ 'start_xpath' ] = xpathRange.start.getPathStr( )
        params[ 'start_word' ] = xpathRange.start.words
        params[ 'start_char' ] = xpathRange.start.chars
        params[ 'end_block' ] = sequenceRange.end.getPaddedPathStr( )
        params[ 'end_xpath' ] = xpathRange.end.getPathStr( )
        params[ 'end_word' ] = xpathRange.end.words
        params[ 'end_char' ] = xpathRange.end.chars
        del params[ 'sequence-range' ]
        del params[ 'xpath-range' ]
        plone = getToolByName(self, 'portal_url').getPortalObject()
        obj_id = plone.generateUniqueId('Annotation')
        
        print "UNIQUE ID", obj_id
        
        #new_id = self.invokeFactory('Annotation', id=obj_id, **params)
        new_id = self.invokeFactory('Annotation', id=obj_id)        
        annotation = getattr(self, new_id)
        annotation.manage_permission("Modify portal content", ["Member", "Anonymous"], 1)
        annotation.Schema()['creators'].set(annotation, self._getUserName())
        if self._getUserName() == 'Anonymous User':
            annotation._owner = (['acl_users'], None)
        annotation.getOwner()
        annotation.update(**params)

        self.REQUEST.RESPONSE.setStatus('Created')
        location = annotation.absolute_url()
        self.REQUEST.RESPONSE.setHeader("location", location)
        return new_id

    security.declarePrivate('_updateAnnotation')
    def _updateAnnotation(self):
        """
        """
        params = {}
        params.update(self.REQUEST)
        params.update(parse_qsl(self.REQUEST.QUERY_STRING))
        annotation = self.get(params['id'], None)
        if not annotation:
            self.REQUEST.RESPONSE.setStatus('BadRequest')
            return
        if params.has_key('link'):
            if  params['link'].startswith("http://"):
                annotation.hyper_link = params['link']
                params.pop('link')
            else:
                if hasattr(annotation, 'hyper_link'):
                    del annotation.hyper_link
            
        annotation.edit(**params)
        if params.has_key("access"):
            workflow = getToolByName(self, 'portal_workflow')
            annotation_workflow = workflow.getWorkflowsFor(annotation)[0]
            status = workflow.getStatusOf("annotation_workflow", annotation)
            if params['access'] == "public" and status['review_state']=="private":
                annotation_workflow.doActionFor(annotation, "publish")
            elif params['access'] == "private" and status['review_state']=="published":
                annotation_workflow.doActionFor(annotation, "retract")
            annotation.reindexObject()
            
        self.REQUEST.RESPONSE.setStatus('NoContent')

    security.declarePrivate('_deleteAnnotation')
    def _deleteAnnotation(self):
        """
        """
        name, value = self.REQUEST.QUERY_STRING.split('=')
        if value:
            self.manage_delObjects(value)
            self.REQUEST.RESPONSE.setStatus('NoContent')
            return
        self.REQUEST.RESPONSE.setStatus('BadRequest') # No id

    security.declarePublic('linkUID')
    def linkUID(self, uid, REQUEST=None):
        """Redirects to the linked document."""
        brains = self.uid_catalog({'UID':uid})
        if not brains:
            return 
        return REQUEST.RESPONSE.redirect(brains[0].getObject().absolute_url())

    
    
registerType(Annotations, PROJECTNAME)
# end of class Annotations

##code-section module-footer #fill in your manual code here
##/code-section module-footer



