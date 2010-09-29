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
