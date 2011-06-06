import interfaces
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from bungeni.alchemist.container import stringKey
from zope.app.component.hooks import getSite
import bungeni.ui.utils as ui_utils
from zope.security.proxy import removeSecurityProxy
from zope.interface import providedBy
from bungeni.alchemist import Session
from bungeni.models.domain import ParliamentaryItem
from bungeni.alchemist.container import stringKey
from bungeni.core.language import get_default_language

def generate_uri(object, event):
    session = Session()
    object = session.merge(removeSecurityProxy(object))    
    uri = "/%s/%s/2001-03-01/%s/%s@/main" % (get_default_language(), object.type, object.registry_number, object.language)
    if object.uri is None:
        object.uri = uri
        print "URI is set to:", uri
    else:
        print "URI already set"
    


class ShowURI(AbsoluteURL):
    
    def __str__(self):
        try:
            return "URI: " + self.context.uri
        except:
            return "URI: no URI"

    __call__ = __str__