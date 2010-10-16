from zope.security.proxy import removeSecurityProxy
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from bungeni.alchemist import Session
from bungeni.transcripts import domain
from bungeni.models import domain as bungeni_domain
from bungeni.transcripts import orm
from bungeni.models.utils import get_db_user
from bungeni.transcripts.utils.misc import get_title_of_user
import sqlalchemy.sql.expression as sql
from lxml import etree
from zope.formlib import form
from zope import schema
from zope import interface
from datetime import timedelta
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
        
        sittings = session.query(bungeni_domain.GroupSitting).join((domain.Assignment, 
                                    bungeni_domain.GroupSitting.sitting_id == domain.Assignment.sitting_id)) \
                .filter(sql.and_(bungeni_domain.GroupSitting.status == 'draft_minutes',
                        domain.Assignment.staff_id == logged_in_user.user_id)).all()
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
            sit = session.query(domain.Sitting).get(sitting.sitting_id)
            sitting.file = sit.media_path
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
        mps = session.query(bungeni_domain.MemberOfParliament).all()
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
                sitting = session.query(bungeni_domain.GroupSitting).get(int(sitting_id))
            print "Sitting ID",sitting_id, "\n";
            for speech in take.iterchildren("speech"):
                s_start_time = speech.get("startTime").split(":")
                s_end_time = speech.get("endTime").split(":")
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
                    transcript = domain.Transcript()
                    transcript.start_date = sitting.start_date+take_start_time + speech_start_time
                    transcript.end_date = sitting.start_date+take_start_time + speech_end_time
                    if speech.get("person_id") == "":
                        transcript.person_name = speech.get("person_name")
                    else:
                        transcript.person_id = int(speech.get("person_id"))
                    transcript.text = speech.text
                    transcript.sitting_id = sitting.sitting_id
                    session.add(transcript)
        session.commit()
