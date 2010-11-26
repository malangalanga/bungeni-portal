from bungeni.ui.browser import BungeniViewlet
from zope.app.pagetemplate import ViewPageTemplateFile
from bungeni.models import domain
from bungeni.alchemist import Session
import sqlalchemy.sql.expression as sql
from sqlalchemy.orm import eagerload
from zc.resourcelibrary import need
class MemberSpeechesViewlet(BungeniViewlet):
    """Speeches of an MP 
    """
    
    view_name = "Speeches"
    view_id = "speeches"
    for_display = True
    render = ViewPageTemplateFile("templates/mp_transcript_viewlet.pt")
    
    def __init__(self, context, request, view, manager):
        super(MemberSpeechesViewlet, self).__init__(
            context, request, view, manager)
        user_id = self.context.user_id
        self.sittings = Session().query(domain.GroupSitting) \
                            .join((domain.Hansard, domain.Hansard.sitting_id == domain.GroupSitting.sitting_id)) \
                            .join((domain.Speech, domain.Speech.hansard_id == domain.Hansard.hansard_id)) \
                            .filter(sql.and_(domain.Speech.person_id == user_id)) \
                            .options( eagerload("group"),
                                      eagerload("hansard"), 
                                      eagerload("hansard.speeches")) \
                            .order_by(domain.Speech.start_date.desc()).all()
        
        for sitting in self.sittings:
            sitting.href = "/business/sittings/obj-%s/hansard" % sitting.sitting_id
            sitting.mp_speeches = []
            for speech in sitting.hansard.speeches:
                if (speech.person_id == user_id):
                    sitting.mp_speeches.append(speech)
    def results(self):
        for sitting in self.sittings:
            yield {"sitting": sitting
                  }
   
    def update(self):
        need("yui-tree")
