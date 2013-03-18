import datetime
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
from zope.formlib import namedtemplate
from zope import schema
from zope import interface
from bungeni.ui.i18n import _
from bungeni.ui.forms.common import set_widget_errors
from bungeni.ui import vocabulary
from bungeni.ui.utils.hansard import get_assigned_staff
from bungeni.ui.utils import url
from bungeni.alchemist import Session
from bungeni.models import domain
from alchemist.catalyst import ui
from zope.traversing.browser import absoluteURL
from zope.component import getMultiAdapter
from zope.security.proxy import removeSecurityProxy
from zope.formlib.form import AddForm, EditForm, PageForm
from zope.app.form.browser import TextWidget
from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser import MultiCheckBoxWidget as _MultiCheckBoxWidget
from zope.component import createObject, getMultiAdapter
from zope.security.proxy import removeSecurityProxy
from sqlalchemy.orm import eagerload
from bungeni.models.utils import get_db_user
import sqlalchemy.sql.expression as sql

from lxml import etree
timedelta = datetime.timedelta

class HansardView(BrowserView):
    template = ViewPageTemplateFile("templates/hansard.pt")
    def __call__(self):
        session = Session()
        trusted = removeSecurityProxy(self.context)
        self.hansard = session.query(domain.Hansard) \
                                .filter(domain.Hansard.sitting_id 
                                                == trusted.sitting_id) \
                                .options(eagerload("media_paths")).all()[0]
        self.hansard.items = session.query(domain.HansardItem) \
                                .filter(domain.HansardItem.hansard_id 
                                              == self.hansard.hansard_id) \
                                .all()
        #import pdb; pdb.set_trace();
        self.duration =  self.context.end_date - self.context.start_date
        rendered = self.render()
        
        return rendered
        
    def render(self):
        return self.template()
      
class EditMediaPath(ui.EditForm):
    class IEditMediaPathForm(interface.Interface):
        web_optimised_video_path = schema.URI(
                            title=u'Web Optimised File URL',
                            description=u'URL of the Web Optimised Media File',
                            required=True)
        audio_only_path = schema.URI(
                            title=u'Audio Only File URL',
                            description=u'URL of the Audio Only Media File',
                            required=False)
        high_quality_video_path = schema.URI(
                            title=u'High Quality Media URL',
                            description=u'URL of the High Quality Media File',
                            required=False)
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(IEditMediaPathForm)
   
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            session = Session()
            trusted = removeSecurityProxy(self.context)
            sitting = session.query(domain.GroupSitting) \
                            .options( eagerload("hansard"),
                            eagerload("hansard.media_paths")).get(trusted.sitting_id) 
            if sitting.hansard.media_paths is not None:
                web_optimised_video_path = sitting.hansard. \
                                    media_paths.web_optimised_video_path
                audio_only_path = sitting.hansard. \
                                        media_paths.audio_only_path
                high_quality_video_path = sitting.hansard. \
                                        media_paths.high_quality_video_path
            else:
                web_optimised_video_path = None
                audio_only_path = None
                high_quality_video_path = None
            
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
        sitting = session.query(domain.GroupSitting).get(trusted.sitting_id)
        if sitting.hansard.media_paths is None:
            media_paths = domain.HansardMediaPaths()
            media_paths.web_optimised_video_path =  data['web_optimised_video_path']    
            media_paths.audio_only_path =  data['audio_only_path']
            media_paths.high_quality_video_path =  data['high_quality_video_path'] 
            media_paths.hansard_id = sitting.hansard.hansard_id
            session.add(media_paths)
        else:
            sitting.hansard.media_paths.web_optimised_video_path =  data['web_optimised_video_path']    
            sitting.hansard.media_paths.audio_only_path =  data['audio_only_path']
            sitting.hansard.media_paths.high_quality_video_path =  data['high_quality_video_path'] 
            session.update(sitting)
        session.commit()
        self._next_url = absoluteURL(self.context, self.request)+"/hansard"
        self.request.response.redirect(self._next_url)
        
    @form.action(_(u"Cancel"))  
    def handle_cancel(self, action, data):
        self._next_url = absoluteURL(self.context, self.request) 
        self.request.response.redirect(self._next_url)

def group_sitting_created(ob, event):
    '''
    Recieves notification that a new sitting has been created and creates
    a hansard for it.
    '''
    session = Session()
    ob = removeSecurityProxy(ob)
    hansard = domain.Hansard()
    hansard.sitting_id = ob.sitting_id
    session.add(hansard)
    session.commit()
        
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
'''
class SpeechBaseForm(PageForm):
    template = ViewPageTemplateFile('templates/empty.pt')
    form_fields = form.Fields(ITranscriptForm) 
    form_fields['start_time'].custom_widget = startTimeWidget
    form_fields['end_time'].custom_widget = endTimeWidget
    form_fields['speech'].custom_widget = speechWidget
    form_fields['person'].custom_widget = personWidget
                
class AddSpeech(AddForm, TranscriptBaseForm):      
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
        transcript.start_date =  data['start_time']                    
        transcript.end_date =  data['end_time']                      
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
        '''
           
class GenerateTakes(PageForm):
    class IGenerateTakes(interface.Interface):
        duration = schema.Int(
            title = _(u"Duration of takes"),
            required = True)
    form_fields = form.Fields(IGenerateTakes)
    template = namedtemplate.NamedTemplate('alchemist.form')
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            duration = None
        self.adapters = {
            self.IGenerateTakes: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)
                    
    def validate(self, action, data):
        errors = super(GenerateTakes, self).validate(action, data)
        if ((len(get_assigned_staff(self.context, "Reporter")) == 0)
            or (len(get_assigned_staff(self.context, "Reader")) == 0)
            or (len(get_assigned_staff(self.context, "Editor")) == 0)):
            errors.append(interface.Invalid(
                _(u"Staff have not been assigned to work on this sitting yet"),
                "duration"))
        return errors
        
    @form.action(_(u"Generate Takes"))
    def handle_generate_takes(self, action, data):
        session = Session()
        trusted = removeSecurityProxy(self.context)
        takes = session.query(domain.Take).filter(
            domain.Take.sitting_id == trusted.sitting_id)
        for t in takes:
            session.delete(t)
        
        sitting = trusted
        current_start_time = sitting.start_date
        sitting_duration = sitting.end_date - sitting.start_date
        take_duration = timedelta(minutes=int(data["duration"]))
        assigned_reporters = get_assigned_staff(self.context, "Reporter")
        assigned_readers = get_assigned_staff(self.context, "Reader")
        assigned_editors = get_assigned_staff(self.context, "Editor")
        c_reporter = 0 
        c_reader = 0
        c_editor = 0
        
        while sitting_duration > timedelta(minutes=0):
            take = domain.Take()
            take.sitting_id = sitting.sitting_id
            if (sitting_duration - take_duration) > timedelta(minutes=0):
                sitting_duration = sitting_duration - take_duration
                take.start_date = current_start_time
                take.end_date = take.start_date + take_duration
                current_start_time = take.end_date
            else:
                take.start_date = current_start_time
                take.end_date = take.start_date + sitting_duration
                sitting_duration = timedelta(minutes=0)
            if c_reporter > len(assigned_reporters)-1:
                c_reporter = 0
                take.reporter_id = assigned_reporters[c_reporter]
            else:
                take.reporter_id = assigned_reporters[c_reporter]
            c_reporter = c_reporter + 1
            
            if c_reader > len(assigned_readers)-1:
                c_reader = 0
                take.reader_id = assigned_readers[c_reader]
            else:
                take.reader_id = assigned_readers[c_reader]
            c_reader = c_reader + 1
            
            if c_editor > len(assigned_editors)-1:
                c_editor = 0
                take.editor_id = assigned_editors[c_editor]
            else:
                take.editor_id = assigned_editors[c_editor]
            c_editor = c_editor + 1
            session.add(take)
        session.commit()
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
            domain.Take.sitting_id == self.context.sitting_id) \
            .order_by(domain.Take.start_date).all()
        if len(takes) > 0:
            self.generated = True
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
        self.request.response.redirect('./hansard')    

def get_title_of_user(user_id):
    session = Session()
    hansard_office = session.query(domain.Office).filter(domain.Office.office_type == 'H').all()
    if len(hansard_office) == 0:
        return None
    query = session.query(domain.GroupMembership).filter(
                sql.and_(domain.GroupMembership.membership_type == 'officemember',
                domain.GroupMembership.active_p == True,
                domain.GroupMembership.user_id == user_id,
                domain.GroupMembership.group_id == hansard_office[0].office_id)
                )
    results = query.all()
    if len(results) == 0:
        return None
    ob = results[0]
    titles = [t.title_name.user_role_name for t in ob.member_titles]
    if "Editor" in titles:
        return "Editor"
    if "Reader" in titles:
        return "Reader"
    if "Reporter" in titles:
        return "Reporter"

class TakesXML(BrowserView):  
    template = ViewPageTemplateFile("templates/takesxml.pt")
    def __call__(self):
        rendered = self.render()
        return rendered
        
    def render(self):
        self.sittings = self.get_sittings()
        self.request.response.setHeader('Content-type', 'text/xml')
        return self.template()
        
    def get_sittings(self):
        session = Session()
        logged_in_user = get_db_user()
        title = get_title_of_user(logged_in_user.user_id)
        
        sittings = session.query(domain.GroupSitting).join((domain.Assignment, 
                                    domain.GroupSitting.sitting_id 
                                             == domain.Assignment.sitting_id)) \
                .filter(sql.and_(domain.GroupSitting.status == 'draft_minutes',
                        domain.Assignment.staff_id == logged_in_user.user_id)) \
                .options( eagerload("hansard"),
                            eagerload("hansard.media_paths")).all()
        for sitting in sittings:
            if title == "Editor":
                takes = session.query(domain.Take)\
                    .filter(sql.and_(domain.Take.editor_id == logged_in_user.user_id,
                    domain.Take.sitting_id == sitting.sitting_id)) \
                    .order_by(domain.Take.start_date).all()
            elif title == "Reader":
                takes = session.query(domain.Take)\
                    .filter(sql.and_(domain.Take.reader_id == logged_in_user.user_id,
                    domain.Take.sitting_id == sitting.sitting_id)) \
                    .order_by(domain.Take.start_date).all()
            elif title == "Reporter":
                takes = session.query(domain.Take)\
                    .filter(sql.and_(domain.Take.reporter_id == logged_in_user.user_id,
                    domain.Take.sitting_id == sitting.sitting_id)) \
                    .order_by(domain.Take.start_date).all()
            for take in takes:
                take.start_time = take.start_date - sitting.start_date
                take.end_time = take.end_date - sitting.start_date
            sitting.takes = takes
            if sitting.hansard.media_paths:
                sitting.file = sitting.hansard.media_paths.web_optimised_video_path
            else:
                sitting.file = ""
            sitting.name = sitting.group.short_name + str(sitting.start_date.strftime('%d-%B-%Y %H:%M'))
        return sittings


class MPSListXML(BrowserView):
    template = ViewPageTemplateFile("templates/mplistxml.pt")
    def __call__(self):
        rendered = self.render()
        return rendered
        
    def render(self):
        self.mps = self.get_mps()
        self.request.response.setHeader('Content-type', 'text/xml')
        return self.template()
        
    def get_mps(self):
        session = Session()
        mps = session.query(domain.MemberOfParliament).all()
        members = []
        for mp in mps:
            members.append(mp.user)
        return members

class SpeechXML(form.PageForm):
    class ISpeechXMLForm(interface.Interface):
        xml = schema.Text(title=u'speech',
                          required=True,
                          description=u"XML of speeches")
                          
    form_fields = form.Fields(ISpeechXMLForm)                      
    def setUpWidgets(self, ignore_request=False):
        class context:
            xml = None
        self.adapters = {
            self.ISpeechXMLForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)
                    
    @form.action(u"Post")     
    def handle_post(self, action, data):
        doc = etree.fromstring(data["xml"])
        session = Session()         
        for take in doc.iterchildren('take'):
            sitting_id = take.get("sittingID")
            t_start_time = take.get("startTime").split(":")
            take_start_time = None
             
            if (len(t_start_time) == 3):
                take_start_time = timedelta(hours=int(t_start_time[0]),
                                            minutes=int(t_start_time[1]),
                                            seconds=int(t_start_time[2]))
            if (sitting_id != ""):
                sitting = session.query(domain.GroupSitting).get(int(sitting_id))
            print "Sitting ID",sitting_id, "\n";
            for s in take.iterchildren("speech"):
                s_start_time = s.get("startTime").split(":")
                s_end_time = s.get("endTime").split(":")
                speech_start_time = None
                speech_end_time = None
                if (len(s_start_time) == 3):
                    speech_start_time = timedelta(hours=int(s_start_time[0]),
                                                  minutes=int(s_start_time[1]),
                                                  seconds=int(s_start_time[2]))
                if (len(s_end_time) == 3):
                    speech_end_time = timedelta(hours=int(s_end_time[0]),
                                                minutes=int(s_end_time[1]),
                                                seconds=int(s_end_time[2]))
                if ( (speech_start_time is not None) and
                     (speech_end_time is not None) and
                     (take_start_time is not None) and
                     (sitting is not None)):
                    speech = domain.Speech() 
                    #hansard_item = domain.HansardItem()
                    speech.start_date =  sitting.start_date+take_start_time + speech_start_time
                    speech.end_date = sitting.start_date+take_start_time + speech_end_time
                    
                    speech.hansard_id = sitting.hansard.hansard_id
                    #import pdb; pdb.set_trace()
                    
                    
                    if s.get("person_id") == "":
                        speech.person_name = s.get("person_name")
                    else:
                        speech.person_id = int(s.get("person_id"))
                    speech.text = s.text
                    session.add(speech)
            for s in take.iterchildren("agenda_item"):
                s_start_time = s.get("startTime").split(":")
                s_end_time = s.get("endTime").split(":")
                agenda_item_start_time = None
                agenda_item_end_time = None
                if (len(s_start_time) == 3):
                    agenda_item_start_time = timedelta(hours=int(s_start_time[0]),
                                                  minutes=int(s_start_time[1]),
                                                  seconds=int(s_start_time[2]))
                if (len(s_end_time) == 3):
                    agenda_item_end_time = timedelta(hours=int(s_end_time[0]),
                                                minutes=int(s_end_time[1]),
                                                seconds=int(s_end_time[2]))
                if ( (agenda_item_start_time is not None) and
                     (agenda_item_end_time is not None) and
                     (take_start_time is not None) and
                     (sitting is not None)):
                    agenda_item = domain.HansardParliamentaryItem() 
                    #hansard_item = domain.HansardItem()
                    agenda_item.start_date =  sitting.start_date+take_start_time + agenda_item_start_time
                    agenda_item.end_date = sitting.start_date+take_start_time + agenda_item_end_time
                    
                    agenda_item.hansard_id = sitting.hansard.hansard_id
                    agenda_item.parliamentary_item_id = int(s.get("person_id"))
                    session.add(agenda_item)
        session.commit()         
            
