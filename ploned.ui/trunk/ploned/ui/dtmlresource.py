
import os

from zope.documenttemplate import HTML
from zope.browserresource.file import FileResource
from zope.browserresource.file import File

class CSSPropertiedDTMLResource(FileResource):
    """ just enough burnt offerings to please the zope2 gods of plone """
    
    _property_file = "base_properties.props"
    _template = None
    _properties = None

    def GET(self):
        """Default document"""
        data = super( CSSPropertiedDTMLResource, self).GET()
        if not data:
            return data
        template = HTML( data )
        
        self.properties['image_url'] = self.request.getApplicationURL() + '/++resource++images'
        data = template( mapping=self.properties, REQUEST=self.request )
        self.request.response.setHeader('Content-Type', 'text/css')
        return data
    
    @property
    def properties( self ):
        if self._properties is not None:
            return self._properties
            
        file = self.chooseContext()
        
        properties_file = os.path.join( os.path.dirname( file.path ), self._property_file )
        d = {}
        if not os.path.exists( properties_file ):
            return d
            
        fh = open( properties_file )
        for line in fh.readlines():
            line = line.strip()
            if not line:
                continue
            k,v = line.split('=')
            k, t =k.split(':')
            d[k]=v
        self._properties = d
        fh.close()
        return d
            
class DTMLResourceFactory(object):

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = CSSPropertiedDTMLResource(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
