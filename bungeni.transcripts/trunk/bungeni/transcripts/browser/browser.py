from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
from zope.formlib import namedtemplate
from zope import schema
from zope import interface
from bungeni.ui.i18n import _
from bungeni.ui.forms.common import set_widget_errors
from ore.alchemist import Session
from bungeni.transcripts import domain
from bungeni.transcripts import orm
from alchemist.catalyst import ui
from zope.traversing.browser import absoluteURL
from zope.component import getMultiAdapter
from bungeni import models
from zope.security.proxy import removeSecurityProxy
from zope.formlib.form import AddForm, EditForm, PageForm
from zope.app.form.browser import TextWidget
from zope.app.form.browser import TextAreaWidget
from bungeni.ui.utils import url
from bungeni.transcripts.interfaces import ITranscriptForm
from zope.component import createObject, getMultiAdapter
class MainView(BrowserView):
    def __call__(self):
        self.group = self.get_group()
        self.group_id = self.context.group_id
        self.sitting_id = self.context.sitting_id
        self.sitting_media_path = self.get_media_path()
        self.duration =  self.context.end_date - self.context.start_date
        return super(MainView, self).__call__()
        
    def get_group(self):
        try:              
            group = self.context.get_group()
        except:
            session = Session()
            group = session.query(models.domain.Group).get(self.context.group_id)
        return group
    
    def get_media_path(self):
        session = Session()
        sitting = session.query(domain.Sitting).filter(domain.Sitting.sitting_id == self.context.sitting_id).first()
        if sitting is not None:
            media_path = sitting.media_path
        else:
            media_path = None
        return media_path
    

class DisplayTranscripts(BrowserView):
    def __call__(self):
        self.transcripts = self.get_transcripts()
        return super(DisplayTranscripts, self).__call__()
    
    def get_transcripts(self):
        session = Session()
        transcripts = session.query(domain.Transcript).filter(domain.Transcript.sitting_id == self.context.sitting_id).order_by(domain.Transcript.start_time)
        #import pdb; pdb.set_trace()
        ts = []
        for transcript in transcripts:
            t = removeSecurityProxy(transcript)
            t.edit_url = "javascript:edit_transcript("+url.absoluteURL(t, self.request)+"/edit_transcript)";
            ts.append(t)
        return transcripts
        
class EditMediaPath(ui.EditForm):
    class IEditMediaPathForm(interface.Interface):
        media_path = schema.URI(
                            title=u'Media URL',
                            description=u'URL of the Media File',
                            required=True)
        
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(IEditMediaPathForm)
    
    def __init__(self, context, request):
        super(EditMediaPath, self).__init__(context, request)
        
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            session = Session()
            trusted = removeSecurityProxy(self.context)
            sitting = session.query(domain.Sitting).get(trusted.sitting_id)
            if sitting is not None:
                media_path = sitting.media_path
            else:
                media_path = None
            
        self.adapters = {
            self.IEditMediaPathForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)
    
    def update(self):
        super(EditMediaPath, self).update()
        set_widget_errors(self.widgets, self.errors)

    def validate(self, action, data):    
        errors = super(EditMediaPath, self).validate(action, data)
        return errors
        
    @form.action(_(u"Save"))  
    def handle_save(self, action, data):
        session = Session()
        trusted = removeSecurityProxy(self.context)
        sitting = session.query(domain.Sitting).get(trusted.sitting_id)
        #import pdb; pdb.set_trace()
        if sitting is None:
            sitting = domain.Sitting()
            sitting.sitting_id =  trusted.sitting_id
            sitting.media_path =  data['media_path']     
            session.add(sitting)
        else:
            sitting.media_path =  data['media_path']
        session.commit()
        #import pdb; pdb.set_trace()
        self._next_url = absoluteURL(self.context, self.request)+"/transcripts"
        self.request.response.redirect(self._next_url)
    @form.action(_(u"Cancel"))  
    def handle_cancel(self, action, data):
        self._next_url = absoluteURL(self.context, self.request) 
        self.request.response.redirect(self._next_url)
        
def startTimeWidget(field, request):
    widget = TextWidget(field, request)
    widget.cssClass = u"start_time_widget"
    return widget
def endTimeWidget(field, request):
    widget = TextWidget(field, request)
    widget.cssClass = u"end_time_widget"
    return widget
def speechWidget(field, request):
    widget = TextAreaWidget(field, request)
    widget.cssClass = u"speech_widget"
    return widget
def personWidget(field, request):
    widget = TextWidget(field, request)
    widget.cssClass = u"person_widget"
    return widget

class TranscriptBaseForm(PageForm):
    template = ViewPageTemplateFile('empty.pt')
    form_fields = form.Fields(ITranscriptForm) 
    form_fields['start_time'].custom_widget = startTimeWidget
    form_fields['end_time'].custom_widget = endTimeWidget
    form_fields['speech'].custom_widget = speechWidget
    form_fields['person'].custom_widget = personWidget
                 
class AddTranscript(AddForm, TranscriptBaseForm):      
    def create(self, data):
        document = createObject(u'ITranscript')
        applyChanges(document, self.form_fields, data)
        return document
        
    def update(self):
        super(AddTranscript, self).update()
        set_widget_errors(self.widgets, self.errors)

    def validate(self, action, data):    
        errors = super(AddTranscript, self).validate(action, data)
        return errors
    
    @form.action(_(u"Save"))
    def handle_save(self, action, data):
        session = Session()
        transcript = domain.Transcript()
        transcript.start_time =  data['start_time']                    
        transcript.end_time =  data['end_time']                      
        transcript.text = data['speech']
        transcript.person = data['person'] 
        transcript.sitting_id = self.context.sitting_id
        session.add(transcript)
        session.commit()
        return 'Save'
    
    @form.action(_(u"Cancel"))
    def handle_cancel(self, action, data):
        return 'Cancel'
        
class EditTranscript(EditForm, TranscriptBaseForm):
    
    def update(self):
        super(EditTranscript, self).update()
        set_widget_errors(self.widgets, self.errors)

    def validate(self, action, data):    
        errors = super(EditTranscript, self).validate(action, data)
        return errors
        
    @form.action(_(u"Save"))  
    def handle_save(self, action, data):
        changed = form.applyChanges(self.context, self.form_fields, data)
        return 'saved'

        
    @form.action(_(u"Cancel"))
    def handle_cancel(self, action, data):
        return 'cancel'
           
class GenerateTakes(PageForm):
    pass
    
class Takes(BrowserView):  
    def __call__(self):
        self.takes = self.get_takes()
        return super(Takes, self).__call__()
    
    def get_takes(self):
        session = Session()
        takes = session.query(domain.Takes).filter(domain.Takes.sitting_id == self.context.sitting_id).order_by(domain.Takes.start_time)
        #import pdb; pdb.set_trace()
        return takes

class Assignment(BrowserView):
    def __call__(self):
        self.available_editors = self.get_available_editors()
        self.available_readers = self.get_available_readers()
        self.available_reporters = self.get_available_reporters()
        self.assigned_editors = self.get_assigned_editors()
        self.assigned_readers = self.get_assigned_readers()
        self.assigned_reporters = self.get_assigned_reporters()
        return super(Takes, self).__call__()
    def get_available_reporters():
        pass 
    def get_available_readers():
        pass
    def get_available_editors():
        pass  
    def get_assigned_reporters():
        pass 
    def get_assigned_readers():
        pass
    def get_assigned_editors():
        pass
           
