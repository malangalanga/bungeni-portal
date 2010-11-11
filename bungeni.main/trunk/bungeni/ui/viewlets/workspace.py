# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Workspace wiewlets

$Id$
"""
log = __import__("logging").getLogger("bungeni.ui.viewlet.workspace")

import sys
import datetime

import sqlalchemy.sql.expression as sql
from sqlalchemy.orm import eagerload

from zope.app.publisher.browser.menu import getMenu
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.viewlet.manager import WeightOrderedViewletManager

from bungeni.alchemist import Session

import bungeni.models.utils  as model_utils
import bungeni.models.domain as domain
from bungeni.ui.interfaces import IWorkspaceContainer, IWorkspaceSectionContext
from bungeni.ui.tagged import get_states
from bungeni.ui import browser
from bungeni.ui import z3evoque
from bungeni.ui.utils import common, misc, debug, url
from bungeni.ui.i18n import _
from bungeni.core.translation import translate_obj
from bungeni.core.workflows.dbutils import getActiveItemSchedule

from ploned.ui.viewlet import StructureAwareViewlet

'''
class ViewTemplateFile(z3evoque.ViewTemplateFile):
    """Evoque file-based template classes with conveniently pre-set preferences
    e.g. the i18n_domain. Viewlets here should use this ViewTemplateFile class.
    """
    i18n_domain = "bungeni.ui"
'''

class WorkspaceViewletManager(WeightOrderedViewletManager):
    
    # evoque
    template = z3evoque.ViewTemplateFile("workspace.html#viewlet_manager")
    
    # zpt
    #template = ViewPageTemplateFile("templates/workspace.pt")

    def update(self):
        super(WorkspaceViewletManager, self).update()
         

class WorkspaceContextNavigation(StructureAwareViewlet):
    
    # evoque
    render = z3evoque.ViewTemplateFile("workspace.html#context_navigation",)
    
    # zpt
    #render = ViewPageTemplateFile("templates/workspace_context_navigation.pt")
    
    def update(self):
        # should only ever be called for contexts with these interfaces
        assert (IWorkspaceContainer.providedBy(self.context) or 
                IWorkspaceSectionContext.providedBy(self.context))
        self.sections = getMenu("workspace_context_navigation", 
                                                self.context, self.request)
        # Append a trailing slash to each workspace viewlet navigation entry so 
        # that the right context is always maintained when using this navigation.
        for section in self.sections:
            section["url"] = url.set_url_context(section["url"])
        
        # get a translated copy of original workspace object
        workspace = translate_obj(
                misc.get_parent_with_interface(self, IWorkspaceContainer))
        self.workspace_title = workspace.full_name

#

class WorkspaceViewlet(browser.BungeniItemsViewlet):
    
    # evoque
    render = z3evoque.ViewTemplateFile("workspace_viewlets.html#items")
    
    # zpt
    #render = ViewPageTemplateFile("templates/workspace_item_viewlet.pt")


''' XXX-INFO-FOR-PLONE - MR - 2010-05-03
class UserIdViewlet(browser.BungeniViewlet):
    """Display the user's principal id."""
    principal_id = None
    
    def __init__(self,  context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__= context
        self.manager = manager
    
    def update(self):
        self.principal_id = model_utils.get_principal_id()
    
    render = ViewPageTemplateFile("../forms/templates/user_id.pt")
'''

''' !+UNUSED(mr, oct-2010)
class QuestionInStateViewlet(WorkspaceViewlet):
    view_id = "_questions"
    view_title= state = None
    
    def _get_items(self):
        #offset = datetime.timedelta(prefs.getNoOfDaysBeforeQuestionSchedule())
        formatter = self.get_date_formatter("date", "long")
        def _q_data_item(q):
            item = {}
            item["qid"]= "q_%s" % q.question_id
            if q.question_number:
                item["subject"] = u"Q %s %s" % (q.question_number, q.short_name)
            else:
                item["subject"] = q.short_name
            item["title"] = q.short_name
            item["result_item_class"] = "workflow-state-%s" % q.status
            item["url"] = url.set_url_context("questions/obj-%s" % q.question_id)
            item["status"] = misc.get_wf_state(q)
            item["status_date"] = formatter.format(q.status_date)
            item["owner"] = "%s %s" %(q.owner.first_name, q.owner.last_name)
            item["type"] = _(q.type)
            item["to"] = q.ministry.short_name
            return item
        return [ _q_data_item(question) for question in self.query.all() ]
    
    def update(self):
        """refresh the query
        """
        session = Session()
        qfilter = (domain.Question.status == self.state)
        questions = session.query(domain.Question).filter(qfilter)
        self.query = questions
        self.items = self._get_items()
'''


class MyGroupsViewlet(WorkspaceViewlet):
    view_id = "my_groups"
    view_title = _("My Groups")
    
    # evoque
    render = z3evoque.ViewTemplateFile("workspace_viewlets.html#groups")
    # ZPT
    #render = ViewPageTemplateFile("templates/workspace_group_viewlet.pt")
    
    def _get_items(self):
        formatter = self.get_date_formatter("date", "long")
        data_list = []
        results = self.query.all()
        
        # if no current parliament, no data
        try:
            parliament_id = model_utils.get_current_parliament().parliament_id
        except: 
            return data_list
        #
        government_id = self.__parent__.government_id
        for result in results:
            data = {}
            data["qid"] = "g_%s" % (result.group_id)
            data["subject"] = result.short_name
            data["title"] = "%s (%s)" % (result.short_name, result.type)
            data["result_item_class"] = "workflow-state-%s" % (result.status)
            _url = "/archive/browse/parliaments/obj-%s" % (parliament_id)
            if type(result) == domain.Parliament:
                data["url"] = url.set_url_context(_url)
                continue
            elif type(result) == domain.Committee:
                #data["url"] = url + "/committees/obj-" + str(result.group_id) 
                data["url"] = url.set_url_context("/groups/%s/%s" % (
                    result.parent_group.group_principal_id,
                    result.group_principal_id))
            elif type(result) == domain.PoliticalGroup:
                data["url"] = url.set_url_context(
                    "%s/politicalgroups/obj-%s" % (_url, result.group_id))
            elif type(result) == domain.Ministry:
                data["url"] = url.set_url_context(
                    "%s/governments/obj-%s/ministries/obj-%s" % (
                        _url, government_id, result.group_id))
            else:
                data["url"] = "#"
            data["status"] = misc.get_wf_state(result)
            data["status_date"] = formatter.format(result.status_date)
            data["owner"] = ""
            data["type"] =  _(result.type)
            data["to"] = ""
            data_list.append(data)
        self.items = data_list
    
    def update(self):
        """refresh the query
        """
        session = Session()
        #user_id = self.__parent__.user_id
        #parliament_id = self.__parent__.context.parliament_id
        group_ids = self.__parent__.user_group_ids
        gfilter = sql.and_(domain.Group.group_id.in_(group_ids),
                            domain.Group.status=="active")
        groups = session.query(domain.Group).filter(gfilter)
        self.query = groups
        self.items = self._get_items()

''' !+UNUSED(mr, oct-2010)
class MotionInStateViewlet(WorkspaceViewlet):
    view_id = "_motions"
    view_title = state = None
    
    def _get_items(self):
        """
        return the data of the query
        """
        data_list = []
        results = self.query.all()
        formatter = self.get_date_formatter("date", "long")
        for result in results:
            data ={}
            data["qid"]= ("m_" + str(result.motion_id))
            data["subject"] = u"M " + str(result.motion_number) + \
                u" " +  result.short_name
            data["title"] = result.short_name
            if result.approval_date:
                data["result_item_class"] = ("workflow-state-" + 
                    result.status  + "sc-after-" + 
                    datetime.date.strftime(result.approval_date, "%Y-%m-%d"))
            else:
                data["result_item_class"] = "workflow-state-" + result.status
            data["url"] = url.set_url_context("motions/obj-" + str(result.motion_id))
            data["status"] = misc.get_wf_state(result)
            data["status_date"] = formatter.format(result.status_date)
            data["owner"] = "%s %s" %(
                result.owner.first_name, result.owner.last_name)
            data["type"] =  _(result.type)
            data["to"] = ""
            data_list.append(data)
        return data_list
    
    def update(self):
        """
        refresh the query
        """
        session = Session()
        motions = session.query(domain.Motion).filter(domain.Motion.status==self.state)
        self.query = motions
        self.items = self._get_items()
'''

class OwnedItemsInStageViewlet(WorkspaceViewlet):
    """Group parliamentary items per stage e.g. action required, in progress, 
    answered/debated, "dead" (withdrawn, elapsed, inadmissible, dropped).
    """
    view_id = "items-in-stage"
    view_title = _("Items in Stage")
    states = []
    types = [
        "motion",
        "question",
        "agendaitem",
        "tableddocument",
        "bill"
    ]
    
    def _get_items(self):
        data_list = []
        results = self.query.all()
        formatter = self.get_date_formatter("date", "long")
        for result in results:
            data = {}
            data["qid"] = ("i-" + str(result.parliamentary_item_id))
            if type(result)==domain.AgendaItem:
                g = u" " + result.group.type + u" " + result.group.short_name
            else:
                g = u"" # !+ g?
            data["subject"] = result.short_name
            data["title"] = result.short_name
            data["result_item_class"] = "workflow-state-" + result.status
            data["url"] = url.set_url_context("%ss/obj-%i" % (
                        result.type, result.parliamentary_item_id))
            data["status"] = misc.get_wf_state(result)
            data["status_date"] = formatter.format(result.status_date)
            data["owner"] = "%s %s" %(result.owner.first_name, result.owner.last_name)
            data["type"] = _(result.type)
            if type(result)==domain.Question:
                data["to"] = result.ministry.short_name
            else:
                data["to"]= u""
            # remember original domain object
            data["id"] = result.parliamentary_item_id
            data["_obj"] = result
            # append processed result item
            data_list.append(data)
        return data_list

    def update(self):
        """Refresh the query.
        """
        session = Session()
        try:
            user_id = self.__parent__.user_id
        except:
            user_id = None
        qfilter = sql.and_(
                        domain.ParliamentaryItem.owner_id==user_id,
                        domain.ParliamentaryItem.status.in_(self.states),
                        domain.ParliamentaryItem.type.in_(self.types))
        self.query = session.query(domain.ParliamentaryItem).filter(qfilter
            ).order_by(domain.ParliamentaryItem.parliamentary_item_id.desc())
        self.items = self._get_items()

class AllItemsInStageViewlet(OwnedItemsInStageViewlet): 

    def update(self):
        """Refresh the query.
        """
        session = Session()
        qfilter = sql.and_(
                domain.ParliamentaryItem.status.in_(self.states),
                domain.ParliamentaryItem.type.in_(self.types)
                    )
        self.query = session.query(domain.ParliamentaryItem).filter(qfilter
            ).order_by(domain.ParliamentaryItem.parliamentary_item_id.desc()) 
        self.items = self._get_items()

class MPItemDraftViewlet(OwnedItemsInStageViewlet): 
    view_id = "items-draft"
    view_title = _("draft items")
    states = \
        get_states("agendaitem", keys=["draft"]) + \
        get_states("motion", keys=["draft"]) + \
        get_states("question", keys=["draft"]) + \
        get_states("tableddocument", keys=["draft"])


class MPItemActionRequiredViewlet(OwnedItemsInStageViewlet): 
    """
    Display all questions and motions that require action
    (e.g. draft, clarification required)
    """
    view_id = "items-action-required"
    view_title = _("to review")
    states = \
        get_states("agendaitem", keys=["clarify_mp"]) + \
        get_states("motion", keys=["clarify_mp"]) + \
        get_states("question", keys=["clarify_mp"]) + \
        get_states("tableddocument", keys=["clarify_mp"])


class MPItemInProgressViewlet(OwnedItemsInStageViewlet):
    """Going through the workflow in clerks/speakers office.
    """
    view_id = "items-in-progress"
    view_title = _("in progress")
    states = \
        get_states("agendaitem", not_tagged=["private", "terminal", "actionmp"]) + \
        get_states("bill", not_tagged=["private", "terminal"]) + \
        get_states("motion", not_tagged=["private", "terminal", "actionmp"]) + \
        get_states("question", not_tagged=["private", "terminal", "actionmp"]) + \
        get_states("tableddocument", not_tagged=["private", "terminal", "actionmp"])


def get_archived_states():
    return \
        get_states("agendaitem", tagged=["terminal"]) + \
        get_states("bill", tagged=["terminal"]) + \
        get_states("motion", tagged=["terminal"]) + \
        get_states("question", tagged=["terminal"]) + \
        get_states("tableddocument", tagged=["terminal"])

class ItemArchiveViewlet(OwnedItemsInStageViewlet):
    view_id = "items-archived"
    view_title = _("archived items")
    states = get_archived_states()

class AllItemArchiveViewlet(AllItemsInStageViewlet):
    view_id = "items-archived"
    view_title = _("Archived Items")
    states = get_archived_states()
    types = [
        "motion",
        "question",
        "agendaitem",
        "tableddocument"
    ]

class ClerkItemActionRequiredViewlet(AllItemsInStageViewlet):
    view_id = "items-action-required"
    view_title = _("to review")
    states = \
        get_states("agendaitem", tagged=["actionclerk"]) + \
        get_states("motion", tagged=["actionclerk"]) + \
        get_states("question", tagged=["actionclerk"]) + \
        get_states("tableddocument", tagged=["actionclerk"])
    types = [
        "motion",
        "question",
        "agendaitem",
        "tableddocument"
    ]

class ClerkItemsWorkingDraftViewlet(AllItemsInStageViewlet):
    view_id = "clerk-items-working-draft"
    view_title = _("draft items")
    states = \
        get_states("agendaitem", keys=["working_draft"]) + \
        get_states("bill", keys=["working_draft"]) + \
        get_states("motion", keys=["working_draft"]) + \
        get_states("question", keys=["working_draft"]) + \
        get_states("tableddocument", keys=["working_draft"])    
class SpeakerItemsWorkingDraftViewlet(ClerkItemsWorkingDraftViewlet):
    view_id = "speaker-items-working-draft"

class SpeakersClerkItemActionRequiredViewlet(ClerkItemActionRequiredViewlet):
    view_id = "clerks-items-action-required"
    view_title = _("pending with the clerk")

class ClerkReviewedItemViewlet(AllItemsInStageViewlet): 
    view_title = _("in progress")
    states = (
        get_states("agendaitem", not_tagged=[
                "private", "terminal", "actionclerk", "scheduled", "approved",
        ]) +
        get_states("bill", not_tagged=[
                "private", "terminal", "scheduled", "approved",
        ]) +
        get_states("motion", not_tagged=[
                "private", "terminal", "actionclerk", "scheduled", "approved",
        ]) +
        get_states("question", not_tagged=[
                "private", "terminal", "actionclerk", "scheduled", "approved",
        ]) +
        get_states("tableddocument", not_tagged=[
                "private", "terminal", "actionclerk", "scheduled", "approved",
        ])
    )
    
class ItemsCompleteViewlet(AllItemsInStageViewlet): 
    view_id = "items-action-required"
    view_title = _("to review")
    states = \
        get_states("agendaitem", keys=["complete"]) + \
        get_states("motion", keys=["complete"]) + \
        get_states("question", keys=["complete"]) + \
        get_states("tableddocument", keys=["complete"])

class ItemsApprovedViewlet(AllItemsInStageViewlet): 
    view_id = "items-approved"
    view_title = _("approved")
    states = \
        get_states("agendaitem", tagged=["approved"]) + \
        get_states("bill", tagged=["approved"]) + \
        get_states("motion", tagged=["approved"]) + \
        get_states("question", tagged=["approved"]) + \
        get_states("tableddocument", tagged=["approved"])

class ItemsPendingScheduleViewlet(AllItemsInStageViewlet): 
    view_id = "items-pending-schedule"
    view_title = _("to be scheduled")
    states = \
        get_states("agendaitem", tagged=["tobescheduled"]) + \
        get_states("bill", tagged=["tobescheduled"]) + \
        get_states("motion", tagged=["tobescheduled"]) + \
        get_states("question", tagged=["tobescheduled"]) + \
        get_states("tableddocument", tagged=["tobescheduled"])

class ItemsScheduledViewlet(AllItemsInStageViewlet):
    # evoque
    render = z3evoque.ViewTemplateFile("workspace_viewlets.html#scheduled")
    view_id = "items-scheduled"
    view_title = _("scheduled")
    states = \
        get_states("agendaitem", keys=["scheduled"]) + \
        get_states("bill", tagged=["scheduled"]) + \
        get_states("motion", keys=["scheduled"]) + \
        get_states("question", keys=["scheduled"]) + \
        get_states("tableddocument", keys=["scheduled"])
    
    def update(self):
        super(ItemsScheduledViewlet, self).update()
        formatter = self.get_date_formatter("dateTime", "medium")
        for d in self.items:
            d["sittings_start"] = []
            d["sittings_status"] = []
            item_schedules = getActiveItemSchedule(d["id"])
            for item_schedule in item_schedules:
                s = item_schedule.sitting
                d["sittings_start"].append(formatter.format(s.start_date))
                d["sittings_status"].append(s.status)
            # past, present, future
            d["css_class"] = None
            if item_schedules:
                today = datetime.datetime.today().date()
                # take "last" sitting date
                startday = item_schedules[0].sitting.start_date.date()
                if today==startday:
                    d["css_class"] = "present"
                elif today>startday:
                    d["css_class"] = "past"
                else:
                    d["css_class"] = "future"
            

class MinistryItemsViewlet(WorkspaceViewlet):
    view_id = "ministry-items"
    view_title = _("questions to the ministry")
    states = None
    response_types = ["O","W"]
    
    def _get_ministry_items(self, ministry):
        session = Session()
        date_formatter = self.get_date_formatter("date", "long")
        def _q_data_item(q):
            item = {}
            item["qid"]= "q_%s" % q.question_id
            if q.question_number:
                item["subject"] = u"Q %s %s (%s)" % (
                                    q.question_number, q.short_name, q.status)
            else:
                item["subject"] = u"%s (%s)" % (q.short_name, q.status)
            item["title"] = u"%s (%s)" % (q.short_name, q.status)
            item["result_item_class"] = "workflow-state-%s" % q.status
            item["url"] = url.set_url_context("questions/obj-%s" % q.question_id)
            item["status"] = misc.get_wf_state(q)
            item["status_date"] = date_formatter.format(q.status_date)
            item["owner"] = "%s %s" %(q.owner.first_name, q.owner.last_name)
            item["type"] = _(q.type)
            if type(q)==domain.Question:
                item["to"] = q.ministry.short_name
            else:
                item["to"]= u""
            return item
        # prepare query for this ministry's questions
        mq_query = session.query(domain.Question).filter(sql.and_(
                domain.Question.ministry_id==ministry.group_id,
                domain.Question.status.in_(self.states),
                domain.Question.response_type.in_(self.response_types)
                ))
        return [ _q_data_item(question) for question in mq_query.all() ]
           
    def update(self):
        session = Session()
        try:
            ministry_ids = [ m.group_id for m in self.__parent__.ministries ]
        except (Exception,):
            debug.log_exc_info(sys.exc_info(), log_handler=log.info)
            ministry_ids = []
        qfilter = domain.Ministry.group_id.in_(ministry_ids)
        ministries = session.query(domain.Ministry).filter(qfilter).order_by(
            domain.Ministry.start_date.desc())
        self.query = ministries
        self.items = [ item for ministry in self.query.all() 
                       for item in self._get_ministry_items(ministry) ]

class MinistryArchiveViewlet(MinistryItemsViewlet):
    view_id = "items-archived"
    view_title = _("archived items")
    # Ministry archive only includes Questions in a public terminal state
    states = get_states("question", 
                    tagged=["public", "terminal"], conjunction="AND")

class OralMinistryQuestionsViewlet(MinistryItemsViewlet):
    view_id = "ministry-oral-questions"
    view_title = _("oral questions")
    states = get_states("question", tagged=["oral"])
    response_types = ["O"]

class WrittenMinistryQuestionsViewlet(MinistryItemsViewlet):
    view_id = "ministry-written-questions"
    view_title = _("written questions")
    states = get_states("question", tagged=["written"])
    response_types = ["W"]

class InProgressMinistryItemsViewlet(MinistryItemsViewlet):
    """
    going through the workflow in clerks/speakers office
    """
    view_id = "items-in-progress"
    view_title = _("in progress")
    states = get_states("question", keys=["response_submitted"])

class DraftSittingsViewlet(WorkspaceViewlet):
    """The "agendas/minutes" tab in the workspace/pi view for the Clerk.
    """
    
    # evoque
    render = z3evoque.ViewTemplateFile("workspace_viewlets.html#sittings")
    
    # zpt
    #render = ViewPageTemplateFile("templates/workspace_sitting_viewlet.pt")

    view_id = "sitting-draft"
    view_title = _("agendas/minutes")
    states = get_states("groupsitting", tagged=["workspace"])
    
    def _get_items(self):
        data_list = []
        results = self.query.all()
        formatter = self.get_date_formatter("date", "long")
        time_formatter = self.get_date_formatter("time", "short")
        for result in results:
            data = {}
            data["subject"] = result.short_name
            # this tab appears in the workspace pi/ view...
            data["url"] = url.set_url_context(
                "../../scheduling/sittings/obj-%i/schedule" % result.sitting_id)
            # Note: same UI is also displayed at: 
            # /business/sittings/obj-%i/schedule % result.sitting_id
            data["items"] = ""
            data["status"] = misc.get_wf_state(result)
            data["status_date"] = formatter.format(result.status_date)
            data["owner"] = ""
            data["type"] =  result.group.type
            data["group"] = u"%s %s" % (
                    result.group.type.capitalize(), result.group.short_name)
            data["time_from_to"] = (
                    time_formatter.format(result.start_date),
                    time_formatter.format(result.end_date))
            data["date"] = formatter.format(result.start_date) 
            if result.venue:
                data["venue"] = _(result.venue.short_name)
            #else:
            #    date["venue"] = ""
            if type(result)==domain.Question:
                data["to"] = result.ministry.short_name
            else:
                data["to"]= ""
            # past, present, future
            today = datetime.datetime.today().date()
            startday = result.start_date.date()
            if today==startday:
                data["css_class"] = "present"
            elif today>startday:
                data["css_class"] = "past"
            else:
                data["css_class"] = "future"
            data_list.append(data)
        return data_list
    
    def update(self):
        """Refresh the query
        """
        session = Session()
        qfilter = domain.GroupSitting.status.in_(self.states)
        sittings = session.query(domain.GroupSitting).filter(
                qfilter).order_by(domain.GroupSitting.start_date.desc()
                    ).options(
                eagerload("group")
                )
        self.query = sittings
        self.items = self._get_items()

