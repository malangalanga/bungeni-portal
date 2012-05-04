from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zope import interface
from zc.resourcelibrary import need
from bungeni.alchemist import Session
from bungeni.hansard.models import domain
from bungeni.models import domain as bungeni_domain
from bungeni.models.interfaces import IGroupSitting
from zope.formlib import form
from zope import schema
from zope.formlib import namedtemplate
from bungeni.ui.i18n import _
from zope.traversing.browser import absoluteURL



class HansardView(BrowserView):
    template = ViewPageTemplateFile("templates/hansard.pt")
    def __call__(self):
        self.context = removeSecurityProxy(self.context)
        return self.render()
        
    def render(self):
        need("hansard-css")
        return self.template()
