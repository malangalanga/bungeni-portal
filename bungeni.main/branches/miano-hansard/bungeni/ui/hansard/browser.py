from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zc.resourcelibrary import need


class HansardView(BrowserView):
    template = ViewPageTemplateFile("templates/hansard.pt")

    def __call__(self):
        self.context = removeSecurityProxy(self.context)
        return self.render()

    def render(self):
        need("hansard-css")
        return self.template()
