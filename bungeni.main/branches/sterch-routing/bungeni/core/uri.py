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
import bungeni.ui.utils as ui_utils

def generate_uri(object, event):
    session = Session()
    #object = session.merge(removeSecurityProxy(object))
    
    # /<section>/<type>/<date>/<registry id>/<language>@/main/
    getSite() 
    if object.type == 'bill':
        uri = "/bungeni/%s/%s/%s/%s/%s@/main/" % ("ke", object.type, object.publication_date, object.registry_number, object.language)
    else:
        uri = "/bungeni/%s/%s/%s/%s/%s@/main/" % ("ke", object.type, object.status_date.date(), object.registry_number, object.language)
    
    if object.uri is None:
        object.uri = uri
    else:
        object.uri = uri

class ShowURI(AbsoluteURL):
    
    def __str__(self):
            return self.context.uri

    __call__ = __str__