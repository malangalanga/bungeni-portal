from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.presentation.presentation import PresentationView

class PresentationView(PresentationView):
    template = ViewPageTemplateFile('presentation.pt')
