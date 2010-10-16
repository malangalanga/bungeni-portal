from bungeni.ui.forms.viewlets import ViewletBase
from zope.app.pagetemplate import ViewPageTemplateFile
from bungeni.transcripts import domain
from bungeni.alchemist import Session

class MemberTranscriptsViewlet(ViewletBase):
    """A transcripts for an MP 
    """
    
    view_name = "Transcripts"
    view_id = "transcripts"
    
    render = ViewPageTemplateFile("templates/mp_transcript_viewlet.pt")
    
    def __init__(self, context, request, view, manager):
        super(MemberTranscriptsViewlet, self).__init__(
            context, request, view, manager)
        user_id = self.context.user_id
        print "MEMBER TRANCRIPTS", user_id
        self.query = Session().query(domain.Transcript).filter(
            sql.and_(
                domain.Transcript.user_id == user_id
            )).order_by(domain.Transcript.start_date.desc())
    
    def results(self):
        for result in self.query.all():
            yield {"start_date": result.start_date,
                   "end_date": result.end_date,
                   "text": result.text
                  }
