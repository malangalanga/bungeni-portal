
from zope.traversing.browser import absoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from bungeni.alchemist.container import stringKey
from zope.app.component.hooks import getSite
import bungeni.ui.utils as ui_utils


class CustomAbsoluteURL(AbsoluteURL):
    section = ""
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/%s/%s/%s' % (base_url, self.section, self.subsection,\
               stringKey(self.context))

    __call__ = __str__

""" Business section
"""
class BusinessAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for business section
    """
    section = "business"
    subsection = ""


class CommitteeBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for committees in business section
    """
    subsection = "committees"
    

class BillBusinessAbsoluteURLView(BusinessAbsoluteURLView):
    """ Custom absolute url for bills in business section
    """
    subsection = "bills"


class QuestionBusinessAbsoluteURLView(BusinessAbsoluteURLView):
    """ Custom absolute url for questions in business section
    """
    subsection = "questions"


class MotionBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for user
    """
    subsection = "motions"
   
    
class TabledDocumentBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for user
    """
    subsection = "tableddocuments"
    
    
class AgendaItemBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for user
    """
    subsection = "agendaitems"

    
""" Members section
"""
"""class MembersAbsoluteURLView(AbsoluteURL):
    
    def __str__(self):
        request = self.request
        return '/members/current/%s' % stringKey(self.context)

    __call__ = __str__
"""

class MembersAbsoluteURLView(CustomAbsoluteURL):
    section = "members"
    subsection = "current"

""" Archives section
"""
class ArchiveAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for business section
    """
    section = "archive/browse"
    subsection = ""


class ParliamentsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for user
    """
    subsection = "parliaments"


class PoliticalGroupsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for user
    """
    subsection = "politicalgroups"
    
    
class ConstituenciesArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for user
    """
    subsection = "constituencies"
    
    
class CommitteesArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for user
    """
    subsection = "committees"
    
    