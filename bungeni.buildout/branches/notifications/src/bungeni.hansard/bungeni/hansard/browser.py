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


class MediaPath(form.EditForm):
    class IEditMediaPathForm(interface.Interface):
        web_optimised_video_path = schema.URI(
                            title=u'Web Optimized Media URL',
                            description=u'URL of the Media File',
                            required=True)
        audio_only_path = schema.URI(
                            title=u'Audio Only Media URL',
                            description=u'URL of the Audio Only Media File',
                            required=False)
        high_quality_video_path = schema.URI(
                            title=u'High Quality Media URL',
                            description=u'URL of High Quality Media File',
                            required=False)
        
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(IEditMediaPathForm)
    
    def setUpWidgets(self, ignore_request=True):
        context = removeSecurityProxy(self.context).media_paths
        self.adapters = {
            self.IEditMediaPathForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)
    
    @form.action(_(u"Save"))  
    def handle_save(self, action, data):
        trusted = removeSecurityProxy(self.context)
        if form.applyChanges(trusted.media_paths, self.form_fields, data, 
                                                                self.adapters):
            session = Session()
            session.add(trusted.media_paths)
            session.flush()
        self._next_url = absoluteURL(self.context, self.request)
        self.request.response.redirect(self._next_url)
        
    @form.action(_(u"Cancel"))  
    def handle_cancel(self, action, data):
        self._next_url = absoluteURL(self.context, self.request) 
        self.request.response.redirect(self._next_url)

