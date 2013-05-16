# !+ CLEAN UP THIS FILE, MINIMALLY AT LEAST THE SRC CODE FORMATTING !

from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.app.component.hooks import getSite
from zope.component import getUtility
import bungeni.ui.utils as ui_utils
from bungeni.alchemist.container import stringKey
from bungeni.alchemist import Session
from bungeni.models.domain import Doc
from bungeni.models.roles import ROLES_DIRECTLY_DEFINED_ON_OBJECTS
from bungeni.core import workspace
from bungeni.ui.utils.common import get_workspace_roles
from bungeni.core.interfaces import IWorkspaceTabsUtility


class CustomAbsoluteURL(AbsoluteURL):
    section = ""
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/%s/%s/%s' % (base_url, self.section, self.subsection,\
               stringKey(self.context))

    __call__ = __str__
    

""" Workspace section
"""

class WorkspaceAbsoluteURLView(AbsoluteURL):
    
    subsection = ''
    
    def __str__(self):
        tabs_utility = getUtility(IWorkspaceTabsUtility)
        domain_class = self.context.__class__
        status = self.context.status
        roles = get_workspace_roles() + ROLES_DIRECTLY_DEFINED_ON_OBJECTS
        tab = None
        for role in roles:
            tab = tabs_utility.get_tab(role, domain_class, status)
            if tab:
                base_url = ui_utils.url.absoluteURL(getSite(), self.request)
                key = workspace.WorkspaceBaseContainer.string_key(self.context)
                return '%s/workspace/my-documents/%s/%s' % (base_url, tab, key)
        else:
            return None
            
    __call__ = __str__


    
""" Members section
"""
class MembersAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for members of parliament in members section
    """
    section = "members"
    subsection = "current"
    
class PoliticalGroupMembersAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for political group in members section
    """    
    section = "members"
    subsection = "political-groups"


''' !+ARCHIVE

""" Archives section
"""
class ArchiveAbsoluteURLView(CustomAbsoluteURL):
    """ Custom absolute url for archive section
    """
    section = "archive/browse"
    subsection = ""


class ParliamentsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for chambers in archive section
    """
    subsection = "chambers"


class PoliticalGroupsArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for political groups in archive section
    """
    subsection = "politicalgroups"


class CommitteesArchiveAbsoluteURLView(ArchiveAbsoluteURLView):
    """ Custom absolute url for committees in archive section
    """
    subsection = "committees"
    
    
class ArchiveSectionParliamentItem(AbsoluteURL):
    """ Custom absolute url for parliament items in archive section
    """
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/archive/browse/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.chamber_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class QuestionArchiveAbsoluteURLView(ArchiveSectionParliamentItem):
    """ Custom absolute url for questions in archive section
    """
    subsection = "questions"
    
    
class ReportArchiveAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for reports in archive section
    """
    subsection = "preports"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/archive/browse/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class TabledDocumentArchiveAbsoluteURLView(ArchiveSectionParliamentItem):
    """ Custom absolute url for tabled documents in archive section
    """
    subsection = "tableddocuments"
    

class MotionArchiveAbsoluteURLView(ArchiveSectionParliamentItem):
    """ Custom absolute url for motions in archive section
    """
    subsection = "motions"
    

class BillArchiveAbsoluteURLView():
    """ Custom absolute url for bills in archive section
    """
    subsection = "bills"

    
class MemberArchiveAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for parliament members in archive section
    """
    subsection = "members"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/archive/browse/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class OfficeArchiveAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for offices in archive section
    """
    subsection = "offices"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/archive/browse/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.parent_group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class AgendaItemArchiveAbsoluteURLView(ArchiveSectionParliamentItem):
    """ Custom absolute url for agenda items in archive section
    """
    subsection = "agendaitems"
'''



""" Admin section
"""
class ParliamentAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for chambers in admin section
    """   
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/chambers/%s' % (base_url, stringKey(self.context))

    __call__ = __str__
    

class AdminSectionParliamentItem(AbsoluteURL):
    """ Custom absolute url for parliament items in admin section
    """
    subsection = ""
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.chamber_id, self.subsection, stringKey(self.context))

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
        return '%s/admin/content/chambers/obj-%s/%s/%s' % \
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
        return '%s/admin/content/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.parent_group_id, self.subsection, stringKey(self.context))

    __call__ = __str__
    
    
class MemberAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for parliament members in admin section
    """
    subsection = "members"
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/chambers/obj-%s/%s/%s' % \
               (base_url, self.context.group_id, self.subsection, stringKey(self.context))

    __call__ = __str__


class OfficeAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for offices in admin section
    """
    
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/offices/%s' % \
               (base_url, stringKey(self.context))

    __call__ = __str__


class AgendaItemAdminAbsoluteURLView(AdminSectionParliamentItem):
    """ Custom absolute url for agenda items in admin section
    """
    subsection = "agenda_items"
    

class UserAdminAbsoluteURLView(AbsoluteURL):
    """ Custom absolute url for users in admin section
    """
    def __str__(self):
        base_url = ui_utils.url.absoluteURL(getSite(), self.request)        
        return '%s/admin/content/users/%s' % (base_url, stringKey(self.context))

    __call__ = __str__
    

