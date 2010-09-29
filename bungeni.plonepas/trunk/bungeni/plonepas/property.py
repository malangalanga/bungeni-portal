import urllib
import httplib2
import simplejson

from OFS.Cache import Cacheable

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.plugins import IUpdatePlugin
from Products.PluggableAuthService.utils import createViewName

from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PlonePAS.sheet import MutablePropertySheet
from utils import connection_url


class PropertyProvider(BasePlugin,Cacheable ):

    def __init__(self, id, title=""):
        self.id = self.id = id
        self.title = title

    def getPropertiesForUser(self, user, request=None):
        """Get property values for a user or group.
        Returns a dictionary of values or a PropertySheet.
        """
        view_name = createViewName('getPropertiesForUser', user)
        cached_info = self.ZCacheable_get(view_name=view_name)
        if cached_info is not None:
            return MutablePropertySheet(self.id, **cached_info)
        data = None
        if user.isGroup():
            http_obj=httplib2.Http()
            query = '/++rest++brs/groups?'
            params = urllib.urlencode({'user_name': user.getUserName()})            
            resp,content = http_obj.request(connection_url()+ query + params, "GET")
            data = simplejson.loads(content)
            
        else:
            http_obj=httplib2.Http()
            query = '/++rest++brs/users?'
            params = urllib.urlencode({'user_name': user.getUserName()})
            resp,content = http_obj.request(connection_url()+ query + params, "GET")
            data = simplejson.loads(content)
            
        if data:
            self.ZCacheable_set(data, view_name=view_name)
            sheet = MutablePropertySheet(self.id, **data)
            return sheet
        
    #
    # IMutablePropertiesPlugin implementation
    #
    def setPropertiesForUser(self, user, propertysheet):
        if user.isGroup():
            pass
                #we do not set any attributes from plone here
        else:
            h=httplib2.Http()
            query = '/++rest++brs/users'
            data = {'login': user.getUserName()}
            params = urllib.urlencode(data)
            resp,content = h.request(connection_url()+ query + params, "GET")
            if propertysheet.getProperty('email'):
                data['email']= propertysheet.getProperty('email')
            if propertysheet.getProperty('notification') != None:
                data['receive_notification'] = propertysheet.getProperty('notification')
        view_name = createViewName('getPropertiesForUser', user) 
        cached_info = self.ZCacheable_invalidate(view_name=view_name)

classImplements(PropertyProvider,
                IPropertiesPlugin,
                IUpdatePlugin,
                IMutablePropertiesPlugin)
