"""Skin Resource Directory

a skin resource directory walks through a stack of layers to find a named resource.

also adds in support for plone's dtml css files 

$Id$
"""
from zope import interface, component

try:
    from zope.browserresource.interfaces import IResource
except ImportError:
    # backwards-compatibility
    from zope.component.interfaces import IResource

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher

from zope.browserresource.directory import DirectoryResource, Directory, _marker

from zope.traversing.browser.absoluteurl import AbsoluteURL

import interfaces
import dtmlresource

class RequestWrapper( object ):
    
    interface.implements( IBrowserRequest )
    
    def __init__( self, request ):
        self._request = request
    def __getattr__( self, name ):
        return getattr( self._request, name )

        
class SkinDirectory(DirectoryResource):

    interface.implements( interfaces.ISkinDirectory )

    layers = ()
        
    def get(self, name, default=_marker):
        value = super( SkinDirectory, self ).get( name, None)
        if value is not None:
            return value
        
        wrapper = RequestWrapper( self.request )
        
        # lookup through the layer stack to find other directory
        # resources that might contain the requested resource.
        for layer in self.layers:
            interface.directlyProvides( wrapper, layer )
            resource_dir = component.queryAdapter(wrapper, name=self.__name__)
            if not ( IResource.providedBy( resource_dir ) \
                and IBrowserPublisher.providedBy( resource_dir ) ):
                continue
            resource = resource_dir.get( name )
            if resource is not None:
                return resource
        raise NotFound( name )

class SkinDirectoryFactory(object):

    def __init__(self, path, checker, name, layers):
        self.__dir = Directory(path, checker, name)
        self.__checker = checker
        self.__name = name
        self.__layers = layers

    def __call__(self, request):
        resource = SkinDirectory(self.__dir, request)
        resource.layers = self.__layers
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

class FileResourceAbsoluteURL(AbsoluteURL):
    def _getContextName(self, context):
        if interfaces.ISkinDirectory.providedBy(context.__parent__):
            return context.__name__.split('/', 1)[-1]
        return context.__name__

class SkinDirectoryAbsoluteURL(AbsoluteURL):
    def _getContextName(self, context):
        return "++resource++%s" % getattr(context, '__name__', None)
