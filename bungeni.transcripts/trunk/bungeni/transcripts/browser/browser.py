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
from bungeni.models import domain as main_domain
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
from bungeni.transcripts.browser import vocabulary
from zope.app.form.browser import MultiCheckBoxWidget as _MultiCheckBoxWidget
from bungeni.transcripts.utils.misc import get_assigned_staff
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
        sitting = session.query(domain.Sitting).filter(domain.Sitting.sitting_id==self.context.sitting_id).first()
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
        transcripts = session.query(domain.Transcript).filter(domain.Transcript.sitting_id==self.context.sitting_id).order_by(domain.Transcript.start_time)
        #import pdb; pdb.set_trace()
        ts = []
        for transcript in transcripts:
            t = removeSecurityProxy(transcript)
            t.edit_url =""
            ts.append(t)
        return ts
        
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
    template = ViewPageTemplateFile('templates/empty.pt')
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
    class IGenerateTakes(interface.Interface):
        duration = schema.Int(
            title = "Duration of takes",
            required = True,
                    )
    form_fields = form.Fields(IGenerateTakes)
    template = namedtemplate.NamedTemplate('alchemist.form')
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            duration = 15
        self.adapters = {
            self.IAssignmentForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)
    
    @form.action(_(u"Generate Takes"))
    def handle_assignment(self, action, data):
        self.request.response.redirect('./takes') 
        
class Takes(BrowserView):  
    template = ViewPageTemplateFile("templates/takes.pt")
    generated = False
    def __call__(self):
        
        rendered = self.render()
        return rendered
        
    def render(self):
        self.takes = self.get_takes()
        return self.template()
        
    def get_takes(self):
        session = Session()
        takes = session.query(domain.Take).filter(
            domain.Take.sitting_id == self.context.sitting_id).order_by(domain.Take.start_time)
        #import pdb; pdb.set_trace()
        return takes

def verticalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"verticalMultiCheckBoxWidget"
    widget.orientation = 'vertical'
    return widget

class Assignment(PageForm):
    def __init__(self, context, request):
        super(Assignment, self).__init__(context, request)
        
    class IAssignmentForm(interface.Interface):
        editors = schema.List(title=u'Editors',
                       required=False,
                       value_type=schema.Choice(
                        vocabulary="ActiveEditors"),
                         )
        readers = schema.List(title=u'Readers',
                       required=False,
                       value_type=schema.Choice(
                       vocabulary="ActiveReaders"),
                         )
        reporters = schema.List(title=u'Reporters',
                       required=False,
                       value_type=schema.Choice(
                       vocabulary="ActiveReporters"),
                         )
    form_fields = form.Fields(IAssignmentForm)
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields['editors'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['readers'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['reporters'].custom_widget = verticalMultiCheckBoxWidget
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            editors = get_assigned_staff(self.context, "Editor")
            readers = get_assigned_staff(self.context, "Reader")
            reporters = get_assigned_staff(self.context, "Reporter")
        self.adapters = {
            self.IAssignmentForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)
        
    #def update(self):
        #super(Assignment, self).update()
        #set_widget_errors(self.widgets, self.errors)   
        
    @form.action(_(u"Assign Staff"))
    def handle_assignment(self, action, data):
        session = Session()
        session.query(domain.Assignment).filter(domain.Assignment.sitting_id == self.context.sitting_id).delete()
        for editor_id in data["editors"]:
            assignment = domain.Assignment()
            assignment.sitting_id = self.context.sitting_id
            assignment.staff_id = editor_id
            session.add(assignment)
        for reader_id in data["readers"]:
            assignment = domain.Assignment()
            assignment.sitting_id = self.context.sitting_id
            assignment.staff_id = reader_id
            session.add(assignment)
        for reporter_id in data["reporters"]:
            assignment = domain.Assignment()
            assignment.sitting_id = self.context.sitting_id
            assignment.staff_id = reporter_id
            session.add(assignment)
        session.commit()
        self.request.response.redirect('./transcripts')    
           
            
