from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zc.resourcelibrary import need


class DebateRecordView(BrowserView):
    template = ViewPageTemplateFile("templates/debate-record.pt")
    transcription_video = None

    def __call__(self):
        self.context = removeSecurityProxy(self.context)
        self.transcription_video = self.get_transctiption_video()
        return self.render()

    def render(self):
        need("debate-css")
        return self.template()

    def get_transctiption_video(self):
        for media in self.context.debate_media:
            if media.media_type == "transcription":
                return media.media_path
        return None
