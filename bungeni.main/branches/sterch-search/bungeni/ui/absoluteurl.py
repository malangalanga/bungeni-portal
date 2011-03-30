
from zope.traversing.browser import absoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from bungeni.alchemist.container import stringKey
from zope.app.component.hooks import getSite
import bungeni.ui.utils as ui_utils
from zope.security.proxy import removeSecurityProxy
from zope.interface import providedBy


class CustomAbsoluteURL(AbsoluteURL):
    section = ""
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/%s/%s/%s/' % (base_url, self.section, self.subsection,\
               stringKey(self.context))

    __call__ = __str__


""" Business section
"""
class BusinessAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for business section
    """
    section = "business"
    subsection = ""


class CommitteeBusinessAbsoluteURLView(BusinessAbsoluteURLView):
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
    """ Custom absolute url for motions in business section
    """
    subsection = "motions"
   
    
class TabledDocumentBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for tabled documents in business section
    """
    subsection = "tableddocuments"
    
    
class AgendaItemBusinessAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for agenda items in business section
    """
    subsection = "agendaitems"

    
""" Members section
"""
class MembersAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for members in members section
    """
    section = "members"
    subsection = "current"

""" Archives section
"""
class ArchiveAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for archive section
    """
    section = "archive/browse"
    subsection = ""


class ParliamentsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for parliaments in archive section
    """
    subsection = "parliaments"


class PoliticalGroupsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for political groups in archive section
    """
    subsection = "politicalgroups"
    
    
class ConstituenciesArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for constituencies in archive section
    """
    subsection = "constituencies"
    
    
class CommitteesArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for committees in archive section
    """
    subsection = "committees"
    
    
""" Admin section
"""
class ParliamentAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for parliaments in admin section
    """   
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/%s' % (base_url, stringKey(self.context))

    __call__ = __str__
    

class AdminSectionParliamentItem(AbsoluteURL):
    """ Custom absolute url for parliament items in admin section
    """
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/obj-%s/%s/%s/' % \
               (base_url, self.context.parliament_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class QuestionAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for questions in admin section
    """
    subsection = "questions"
    
    
class ReportAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for reports in admin section
    """
    subsection = "preports"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/obj-%s/%s/%s/' % \
               (base_url, self.context.group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class TabledDocumentAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for tabled documents in admin section
    """
    subsection = "tableddocuments"
    

class MotionAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for motions in admin section
    """
    subsection = "motions"
    

class BillAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for bills in admin section
    """
    subsection = "bills"
    
    
class CommitteeAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for committees in admin section
    """
    subsection = "committees"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/obj-%s/%s/%s/' % \
               (base_url, self.context.parent_group_id, self.subsection, stringKey(self.context))

    __call__ = __str__
    
    
class MemberOfParliamentAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for parliament members in admin section
    """
    subsection = "parliamentmembers"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/obj-%s/%s/%s/' % \
               (base_url, self.context.group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class OfficeAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for offices in admin section
    """
    subsection = "offices"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parliaments/obj-%s/%s/%s/' % \
               (base_url, self.context.parent_group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class AgendaItemAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for agenda items in admin section
    """
    subsection = "agendaitems"
    

class UserAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for users in admin section
    """
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/users/%s/' % (base_url, stringKey(self.context))

    __call__ = __str__
    

class PoliticalPartyAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for users in admin section
    """
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/parties/%s/' % (base_url, stringKey(self.context))

    __call__ = __str__