# -*- coding: utf-8 -*-
#
# File: AnnotationAdaptorAndView
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

from Products.Five import BrowserView
from Products.Archetypes.atapi import *
from zope import interface
from Products.Marginalia.interfaces.IAnnotatable import IAnnotatable, IAnnotatableAdaptor

class AnnotationView(BrowserView):
    """Annotation View Class. """

    def getAnnotatedUrl(self, url):
        """Returns annotated url."""
        obj = IAnnotatableAdaptor(self.context)
        return obj.getAnnotatedUrl(url)


    def isAnnotatable(self):
        """
        """
        obj = IAnnotatableAdaptor(self.context)
        return obj.isAnnotatable()

class AnnotationAdaptor(object):
    """
    """
    interface.implements(IAnnotatable)
    #adapt(IAnnotatableAdaptor)

    def __init__(self, context):
        self.context = context

    def getAnnotatedUrl(self, url ):
        """Returns annotated url."""        
        x = url.find( '/annotate' )
        if -1 != x:
            url = url[ : x ]
        return url

    def isAnnotatable(self):
        """
        """
        return True
