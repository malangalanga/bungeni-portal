# -*- coding: utf-8 -*-
#
# File: AnnotatableDocument.py
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.document import ATDocument
from Products.Marginalia.config import *

schema = BaseSchema.copy() + \
         getattr(ATDocument, 'schema', Schema(())).copy()

class AnnotatableDocument(BaseContent, ATDocument):
    """
    Sample document that uses the Annotation Adaptor.
    """
    security = ClassSecurityInfo()
    archetype_name = meta_type = portal_type = 'AnnotatableDocument'

    filter_content_types = 0
    global_allow = 1
    _at_rename_after_creation = True

    schema = schema    

registerType(AnnotatableDocument, PROJECTNAME)

