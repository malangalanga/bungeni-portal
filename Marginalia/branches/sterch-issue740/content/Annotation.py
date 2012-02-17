# -*- coding: utf-8 -*-
#
# File: Annotation.py
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Marginalia.config import *
from Products.Marginalia.tools.SequenceRange import SequenceRange, SequencePoint
from Products.Marginalia.tools.XPathRange import XPathRange, XPathPoint
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *

##code-section module-header #fill in your manual code here
from DateTime import DateTime
##/code-section module-header

schema = Schema((

    StringField(
        name='url',
        widget=StringWidget(
            label='Url',
            label_msgid='Marginalia_label_url',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='start_block',
        widget=StringWidget(
            label='Start Block',
            label_msgid='Marginalia_label_start_block',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='start_xpath',
        widget=StringWidget(
            label='Start XPath',
            label_msgid='Marginalia_label_start_xpath',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='start_word',
        widget=StringWidget(
            label='Start Word',
            label_msgid='Marginalia_label_start_word',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='start_char',
        widget=StringWidget(
            label='start_char',
            label_msgid='Marginalia_label_start_char',
            i18n_domain='Marginalia',
        )
    ),


    StringField(
        name='end_block',
        widget=StringWidget(
            label='End Block',
            label_msgid='Marginalia_label_end_block',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='end_xpath',
        widget=StringWidget(
            label='End XPath',
            label_msgid='Marginalia_label_end_xpath',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='end_word',
        widget=StringWidget(
            label='End Word',
            label_msgid='Marginalia_label_end_word',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='end_char',
        widget=StringWidget(
            label='End Char',
            label_msgid='Marginalia_label_end_char',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='note',
        widget=StringWidget(
            label='Note',
            label_msgid='Marginalia_label_note',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='access',
        widget=StringWidget(
            label='Access',
            label_msgid='Marginalia_label_access',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='status',
        widget=StringWidget(
            label='Status',
            label_msgid='Marginalia_label_status',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='action',
        widget=StringWidget(
            label='Action',
            label_msgid='Marginalia_label_action',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='edit_type',
        widget=StringWidget(
            label='Action',
            label_msgid='Marginalia_label_action',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='quote',
        widget=StringWidget(
            label='Quote',
            label_msgid='Marginalia_label_quote',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='quote_title',
        widget=StringWidget(
            label='Quote_title',
            label_msgid='Marginalia_label_quote_title',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
        name='quote_author',
        widget=StringWidget(
            label='Quote_author',
            label_msgid='Marginalia_label_quote_author',
            i18n_domain='Marginalia',
        )
    ),

    StringField(
		name ='link_title',
		widget=StringWidget(
			label='Link_title',
			label_msgid='Marginalia_label_link_title',
			il8n_domain='Marginalia',
		)
	),

    ComputedField(
        name='indexed_url',
        index="FieldIndex",
        widget=ComputedField._properties['widget'](
            label='Indexed_url',
            label_msgid='Marginalia_label_indexed_url',
            i18n_domain='Marginalia',
        )
    ),
    ReferenceField('link', 
                   multiValued=0,
                   allowed_types=('ATDocument','ATFile', 'Article', 'AnnotatableDocument'),
                   relationship='referenceLink1',
                   widget=ReferenceBrowserWidget(
                       label="Reference Link",
                       default_search_index='SearchableText',
                       description='Use the browse button to link another document.'
         )
    ),
),
)

##code-section after-local-schema #fill in your manual code here
schema += Schema(( ComputedField( name='title', accessor='Title',),),)
##/code-section after-local-schema

Annotation_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Annotation(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Annotation'

    meta_type = 'Annotation'
    portal_type = 'Annotation'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'Annotation.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Annotation"
    typeDescMsgId = 'description_edit_annotation'

    _at_rename_after_creation = False

    schema = Annotation_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getUserName')
    def getUserName(self):
        # XXX haaaack replace with a view class ..
        return self.getOwner().getUserName()

    security.declarePublic('Title')
    def Title(self):
        return self.getNote()

    security.declarePublic('Description')
    def Description(self):
        return '"%s" annotated this text:\n\n"%s"\n\nas follows:\n\n"%s"' % ( self.getUserName(), self.getQuote(), self.getNote() )

    security.declarePublic('SearchableText')
    def SearchableText(self):
        """Returns searchable text for the annotation."""
        return self.getNote()

    security.declarePublic('getEditType')
    def getEditType(self):
        """Returns edit type for the annotation. (Insert/Delete/Comment/Replace)"""
        return self.getEdit_type()

    security.declarePublic('getIndexed_url')
    def getIndexed_url(self):
        """ There may be more than one annotatable area on a page,
        identified by fragment (#1, #2, ...). Annotations are queried
        per page (#*), so catalog under the page URL.

        Note that the URL includes the server name, so if the server is
        accessed with different names, annotations will be partitioned
        per name.
        
        TODO: Use config settings to strip server name.
        """
        url = self.getUrl()
        if url.find('#') != -1:
            url = url[:url.index('#')]
        return url

    security.declarePublic( 'getLink' )
    def getLink(self):
        """Returns the reference link."""
        if hasattr(self, 'hyper_link'):
            return self.hyper_link
        return self.schema.get('link').get(self)
    
        
    security.declarePublic( 'getSequenceRange' )
    def getSequenceRange( self ):
        startBlock = self.getStart_block( )
        startWord = self.getStart_word( )
        startChar = self.getStart_char( )
        endBlock = self.getEnd_block( )
        endWord = self.getEnd_word( )
        endChar = self.getEnd_char( )
        sequenceRange = SequenceRange( )
        sequenceRange.start = SequencePoint( startBlock, startWord, startChar )
        sequenceRange.end = SequencePoint( endBlock, endWord, endChar )
        return sequenceRange
        
    security.declarePublic( 'getXPathRange' )
    def getXPathRange( self ):
        startXPath = self.getStart_xpath( )
        startWord = self.getStart_word( )
        startChar = self.getStart_char( )
        endXPath = self.getEnd_xpath( )
        endWord = self.getEnd_word( )
        endChar = self.getEnd_char( )
        xpathRange = XPathRange( )
        xpathRange.start = XPathPoint( startXPath, startWord, startChar )
        xpathRange.end = XPathPoint( endXPath, endWord, endChar )
        return xpathRange


registerType(Annotation, PROJECTNAME)
# end of class Annotation

##code-section module-footer #fill in your manual code here
##/code-section module-footer



