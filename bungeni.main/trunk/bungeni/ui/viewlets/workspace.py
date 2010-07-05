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
from zope.viewlet import viewlet
from zope.viewlet.manager import WeightOrderedViewletManager

from ore.alchemist import Session

from bungeni.core.workflows.motion import states as motion_wf_state 
from bungeni.core.workflows.agendaitem import states as agendaitem_wf_state
from bungeni.core.workflows.groupsitting import states as sitting_wf_state

import bungeni.models.utils  as model_utils
import bungeni.models.domain as domain
from bungeni.models.interfaces import ICommittee
from bungeni.ui.interfaces import IWorkspaceContainer, IWorkspaceSectionContext
from bungeni.ui.tagged import get_states
from bungeni.ui import z3evoque
from bungeni.ui.utils import common, misc, debug
from bungeni.ui.i18n import _
from bungeni.core.translation import translate_obj

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
        self.devmode = common.has_feature("devmode")
         

class WorkspaceContextNavigation(StructureAwareViewlet):
    
    # evoque
    render = z3evoque.ViewTemplateFile("workspace.html#context_navigation")
    
    # zpt
    #render = ViewPageTemplateFile('templates/workspace_context_navigation.pt')
    
    def update(self):
        # should only ever be called for contexts with these interfaces
        assert (IWorkspaceContainer.providedBy(self.context) or 
                IWorkspaceSectionContext.providedBy(self.context))
        self.sections = getMenu("workspace_context_navigation", 
                                                self.context, self.request)
        # get a translated copy of original workspace object
        workspace = translate_obj(
                misc.get_parent_with_interface(self, IWorkspaceContainer))
        self.workspace_title = workspace.full_name

#

class ViewletBase(viewlet.ViewletBase):
    render = ViewPageTemplateFile('templates/workspace_item_viewlet.pt')

''' XXX-INFO-FOR-PLONE - MR - 2010-05-03
class UserIdViewlet(viewlet.ViewletBase):
    """Display the user's principal id."""
    principal_id = None
    
    def __init__(self,  context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__= context
        self.manager = manager
    
    def update(self):
        self.principal_id = model_utils.get_principal_id()
    
    render = ViewPageTemplateFile('../forms/templates/user_id.pt')
'''

class QuestionInStateViewlet(ViewletBase):
    name = state = None
    list_id = "_questions"
    
    def getData(self):
        """return the data of the query
        """
        #offset = datetime.timedelta(prefs.getNoOfDaysBeforeQuestionSchedule())
        date_formatter = self.request.locale.dates.getFormatter('date', 'short')
        def _q_data_item(q):
            item = {}
            item['qid']= 'q_%s' % q.question_id
            if q.question_number:
                item['subject'] = u'Q %s %s' % (q.question_number, q.short_name)
            else:
                item['subject'] = q.short_name
            item['title'] = q.short_name
            item['result_item_class'] = 'workflow-state-%s' % q.status
            item['url'] = 'questions/obj-%s' % q.question_id
            item['status'] = misc.get_wf_state(q)
            item['status_date'] = date_formatter.format(q.status_date)
            item['owner'] = "%s %s" %(q.owner.first_name, q.owner.last_name)
            item['type'] = _(q.type)
            item['to'] = q.ministry.short_name
            return item
        return [ _q_data_item(question) for question in self.query.all() ]
    
    def update(self):
        """refresh the query
        """
        session = Session()
        qfilter = (domain.Question.status==self.state)
        questions = session.query(domain.Question).filter(qfilter)
        self.query = questions


class MyGroupsViewlet(ViewletBase):
    name = _("My Groups")
    list_id = "my_groups"
    render = ViewPageTemplateFile('templates/workspace_group_viewlet.pt')
    
    def getData(self):
        """Return the data of the query
        """
        formatter = self.request.locale.dates.getFormatter('date', 'short')
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
            data['qid']= ('g_' + str(result.group_id))
            data['subject'] = result.short_name
            data['title'] = result.short_name  + ' (' + result.type + ')'
            data['result_item_class'] = 'workflow-state-' + result.status
            url = "/archive/browse/parliaments/obj-" + str(parliament_id) 
            if type(result)==domain.Parliament:
                data['url'] = url
                continue
            elif type(result)==domain.Committee:
                #data['url'] = url + '/committees/obj-' + str(result.group_id) 
                data['url'] = ('/groups/' + 
                    result.parent_group.group_principal_id + 
                    '/' + result.group_principal_id)
            elif type(result)==domain.PoliticalGroup:
                data['url'] = url + '/politicalgroups/obj-' + str(result.group_id)
            elif type(result)==domain.Ministry:
                data['url'] = url + ('/governments/obj-%s/ministries/obj-%s' % (
                        str(government_id), str(result.group_id)))
            else:
                data['url'] = '#'
            data['status'] = misc.get_wf_state(result)
            data['status_date'] = formatter.format(result.status_date)
            data['owner'] = ""
            data['type'] =  _(result.type)
            data['to'] = u""
            data_list.append(data)
        return data_list
    
    def update(self):
        """refresh the query
        """
        session = Session()
        #user_id = self.__parent__.user_id
        #parliament_id = self.__parent__.context.parliament_id
        group_ids = self.__parent__.user_group_ids
        gfilter = sql.and_(domain.Group.group_id.in_(group_ids),
                            domain.Group.status=='active')
        groups = session.query(domain.Group).filter(gfilter)
        self.query = groups


class MotionInStateViewlet(ViewletBase):
    name = state = None
    list_id = "_motions"
    def getData(self):
        """
        return the data of the query
        """
        data_list = []
        results = self.query.all()
        formatter = self.request.locale.dates.getFormatter('date', 'short')
        for result in results:
            data ={}
            data['qid']= ('m_' + str(result.motion_id))
            data['subject'] = u'M ' + str(result.motion_number) + u' ' +  result.short_name
            data['title'] = result.short_name
            if result.approval_date:
                data['result_item_class'] = ('workflow-state-' + 
                    result.status  + 'sc-after-' + 
                    datetime.date.strftime(result.approval_date, '%Y-%m-%d'))
            else:
                data['result_item_class'] = 'workflow-state-' + result.status
            data['url'] = 'motions/obj-' + str(result.motion_id)
            data['status'] = misc.get_wf_state(result)
            data['status_date'] = formatter.format(result.status_date)
            data['owner'] = "%s %s" %(result.owner.first_name, result.owner.last_name)
            data['type'] =  _(result.type)
            data['to'] = ""
            data_list.append(data)
        return data_list
    
    
    def update(self):
        """
        refresh the query
        """
        session = Session()
        motions = session.query(domain.Motion).filter(domain.Motion.status==self.state)
        self.query = motions


class SubmittedMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name = motion_wf_state[u"submitted"].title
    state = motion_wf_state[u"submitted"].id
    list_id = "submitted_motions"


class ReceivedMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name = motion_wf_state[u"received"].title
    state = motion_wf_state[u"received"].id
    list_id = "received_motions"

class CompleteMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name = motion_wf_state[u"complete"].title
    state = motion_wf_state[u"complete"].id
    list_id = "complete_motions"
    
   

class ClarifyMpMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name = motion_wf_state[u"clarify_mp"].title
    state = motion_wf_state[u"clarify_mp"].id
    list_id = "clarify_mp_motions"
    
class ClarifyClerkMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name = motion_wf_state[u"clarify_clerk"].title
    state = motion_wf_state[u"clarify_clerk"].id
    list_id = "clarify_clerk_motions"

class DeferredMotionViewlet(MotionInStateViewlet):
    """
    display the submitted Motions
    """
    name =  motion_wf_state[u"deferred"].title
    state = motion_wf_state[u"deferred"].id
    list_id = "deferred_motions"
    
    
    
class AdmissibleMotionViewlet(MotionInStateViewlet):
    """
    display the admissible Motions
    """
    name = motion_wf_state[u"admissible"].title
    state = motion_wf_state[u"admissible"].id
    list_id = "admissible_motions"
    
''' !+ unused:
from bungeni.core.workflows.bill import states as bill_wf_state
class BillItemsViewlet(ViewletBase): 
    """
    Display all bills that can be scheduled for a parliamentary sitting
    """
    name  = _(u"Bills")
    list_id = "schedule_bills"
    def getData(self):
        """
        return the data of the query
        """
        data_list = []
        results = self.query.all()
        formatter = self.request.locale.dates.getFormatter('date', 'short')
        for result in results:
            data ={}
            data['qid']= ('b_' + str(result.bill_id))
            data['subject'] = result.short_name
            data['title'] = result.short_name
            data['result_item_class'] = ('workflow-state-' + result.status)
            data['url'] = '%ss/obj-%i' %(result.type, result.parliamentary_item_id)
            data['status'] = misc.get_wf_state(result)
            data['status_date'] = formatter.format(result.status_date)
            data['owner'] = "%s %s" %(result.owner.first_name, result.owner.last_name)
            data['type'] =  _(result.type)
            data['to'] = ""
            data_list.append(data)
        return data_list
    
    def update(self):
        """
        refresh the query
        """
        session = Session()
        bills = session.query(domain.Bill).filter(domain.Bill.status.in_([
            bill_wf_state[u"gazetted"].id,
            bill_wf_state[u"first_reading"].id ,
            bill_wf_state[u"first_reading_adjourned"].id,
            bill_wf_state[u"second_reading"].id,
            bill_wf_state[u"second_reading_adjourned"].id,
            bill_wf_state[u"whole_house_adjourned"].id,
            bill_wf_state[u"house_pending"].id,
            bill_wf_state[u"third_reading"].id,
            bill_wf_state[u"third_reading_adjourned"].id
        ] ))
        self.query = bills
'''

class OwnedItemsInStageViewlet(ViewletBase):
    """Group parliamentary items per stage e.g. action required, in progress, 
    answered/debated, 'dead' (withdrawn, elapsed, inadmissible, dropped).
    """
    name = "Items in Stage"
    states = []
    list_id = "items-in-stage"
    types = ['motion',
            'question',
            'agendaitem',
            'tableddocument',
            'bill']
    
    def getData(self):
        """Return the data of the query.
        """
        data_list = []
        results = self.query.all()
        formatter = self.request.locale.dates.getFormatter('date', 'short')
        for result in results:
            data = {}
            data['qid']= ('i-' + str(result.parliamentary_item_id))
            if type(result)==domain.AgendaItem:
                g = u' ' + result.group.type + u' ' + result.group.short_name
            else:
                g = u'' # !+ g?
            data['subject'] = result.short_name
            data['title'] = result.short_name
            data['result_item_class'] = 'workflow-state-' + result.status
            data['url'] = '%ss/obj-%i' % (
                        result.type, result.parliamentary_item_id)
            data['status'] = misc.get_wf_state(result)
            data['status_date'] = formatter.format(result.status_date)
            data['owner'] = "%s %s" %(result.owner.first_name, result.owner.last_name)
            data['type'] =  _(result.type)
            if type(result)==domain.Question:
                data['to'] = result.ministry.short_name
            else:
                data['to']= u""
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
            


class MPItemDraftViewlet(OwnedItemsInStageViewlet): 
    name = _("draft items")
    states = [motion_wf_state[u"draft"].id,
        agendaitem_wf_state[u"draft"].id,
        ] + \
        get_states("question", keys=["draft"]) + \
        get_states("tableddocument", keys=["draft"])
    list_id = "items-draft"


class MPItemActionRequiredViewlet(OwnedItemsInStageViewlet): 
    """
    Display all questions and motions that require action
    (e.g. draft, clarification required)
    """
    name = _("to review")
    states = [motion_wf_state[u"clarify_mp"].id,
        agendaitem_wf_state[u"clarify_mp"].id,
        ] + \
        get_states("question", keys=["clarify_mp"]) + \
        get_states("tableddocument", keys=["clarify_mp"])
    list_id = "items-action-required"


    

class MPItemInProgressViewlet(OwnedItemsInStageViewlet):
    """
    going through the workflow in clerks/speakers office
    """
    name = _("in progress")
    states = [
        motion_wf_state[u"submitted"].id,
        motion_wf_state[u"received"].id,
        motion_wf_state[u"complete"].id,
        motion_wf_state[u"clarify_clerk"].id,
        motion_wf_state[u"debate_adjourned"].id,
        motion_wf_state[u"deferred"].id,
        motion_wf_state[u"scheduled"].id,
        agendaitem_wf_state[u"submitted"].id,
        agendaitem_wf_state[u"received"].id,
        agendaitem_wf_state[u"complete"].id,
        agendaitem_wf_state[u"clarify_clerk"].id,
        agendaitem_wf_state[u"deferred"].id,
        agendaitem_wf_state[u"scheduled"].id,
        agendaitem_wf_state[u"debate_adjourned"].id,
        ] + \
        get_states("bill", not_tagged=["private", "terminal"]) + \
        get_states("question", not_tagged=["private", "terminal"]) + \
        get_states("tableddocument", not_tagged=["private", "terminal"])
    list_id = "items-in-progress"

def get_archived_states():
    return [
        agendaitem_wf_state[u"debated"].id,
        agendaitem_wf_state[u"dropped"].id,
        agendaitem_wf_state[u"withdrawn"].id,
        agendaitem_wf_state[u"elapsed"].id,
        agendaitem_wf_state[u"inadmissible"].id,
        motion_wf_state[u"withdrawn"].id,
        motion_wf_state[u"withdrawn_public"].id,
        motion_wf_state[u"elapsed"].id,
        motion_wf_state[u"inadmissible"].id,
        motion_wf_state[u"dropped"].id,
        motion_wf_state[u"adopted"].id,
        motion_wf_state[u"adopted_amendments"].id,
        motion_wf_state[u"rejected"].id,
        ] + \
        get_states("bill", tagged=["terminal"]) + \
        get_states("question", tagged=["terminal"]) + \
        get_states("tableddocument", tagged=["terminal"])

class ItemArchiveViewlet(OwnedItemsInStageViewlet):
    name = _("archived items")
    states = get_archived_states()
    list_id = "items-archived"

class AllItemArchiveViewlet(AllItemsInStageViewlet):
    types = ['motion',
            'question',
            'agendaitem',
            'tableddocument']
    name = _("Archived Items AllItemArchiveViewlet")
    states = get_archived_states()
    list_id = "items-archived"

class ClerkItemActionRequiredViewlet(AllItemsInStageViewlet):
    types = ['motion',
            'question',
            'agendaitem',
            'tableddocument']
    name = _("to review")
    states = [
        agendaitem_wf_state[u"submitted"].id,
        agendaitem_wf_state[u"received"].id,
        agendaitem_wf_state[u"clarify_clerk"].id,
        motion_wf_state[u"submitted"].id,
        motion_wf_state[u"received"].id,
        motion_wf_state[u"clarify_clerk"].id,
        ] + \
        get_states("question", tagged=["actionclerk"]) + \
        get_states("tableddocument", tagged=["actionclerk"])
    list_id = "items-action-required"

class ClerkItemsWorkingDraftViewlet(AllItemsInStageViewlet):
    name = _("draft items")
    states = [motion_wf_state[u"working_draft"].id,
        agendaitem_wf_state[u"working_draft"].id,
        ] + \
        get_states("bill", keys=["working_draft"]) + \
        get_states("question", keys=["working_draft"]) + \
        get_states("tableddocument", keys=["working_draft"])    
    list_id = "clerk-items-working-draft"
class SpeakerItemsWorkingDraftViewlet(ClerkItemsWorkingDraftViewlet):
    list_id = "speaker-items-working-draft"

class SpeakersClerkItemActionRequiredViewlet(ClerkItemActionRequiredViewlet):
    name = _("pending with the clerk")
    list_id = "clerks-items-action-required"

class ClerkReviewedItemViewlet(AllItemsInStageViewlet): 
    name = _("in progress")
    states = [
        motion_wf_state[u"complete"].id,
        agendaitem_wf_state[u"complete"].id,
        motion_wf_state[u"clarify_mp"].id,
        agendaitem_wf_state[u"clarify_mp"].id,
        motion_wf_state[u"deferred"].id,
        motion_wf_state[u"scheduled"].id,
        agendaitem_wf_state[u"deferred"].id,
        agendaitem_wf_state[u"scheduled"].id,
        ] + \
        get_states("bill", not_tagged=["private", "terminal"]) + \
        get_states("question", 
            not_tagged=["private", "terminal", "actionclerk"]) + \
        get_states("tableddocument", 
            not_tagged=["private", "terminal", "actionclerk"])
    
class ItemsCompleteViewlet(AllItemsInStageViewlet): 
    name = _("to review")
    states = [
        motion_wf_state[u"complete"].id,
        agendaitem_wf_state[u"complete"].id,
        ] + \
        get_states("question", keys=["complete"]) + \
        get_states("tableddocument", keys=["complete"])
    list_id = "items-action-required"

class ItemsApprovedViewlet(AllItemsInStageViewlet): 
    name = _("approved")
    states = [
        agendaitem_wf_state[u"admissible"].id,
        agendaitem_wf_state[u"deferred"].id,
        motion_wf_state[u"admissible"].id,
        motion_wf_state[u"deferred"].id,
        ] + \
        get_states("bill", keys=["approved"]) + \
        get_states("question", keys=["admissible", "deferred"]) + \
        get_states("tableddocument", keys=["admissible"])
    list_id = "items-approved"

class ItemsPendingScheduleViewlet(AllItemsInStageViewlet): 
    name = _("to be scheduled")
    states = [
        agendaitem_wf_state[u"schedule_pending"].id,
        agendaitem_wf_state[u"debate_adjourned"].id,
        motion_wf_state[u"schedule_pending"].id,
        motion_wf_state[u"debate_adjourned"].id,
        ] + \
        get_states("bill", tagged=["tobescheduled"]) + \
        get_states("question", tagged=["tobescheduled"]) + \
        get_states("tableddocument", tagged=["tobescheduled"])
    list_id = "items-pending-schedule"

class ItemsScheduledViewlet(AllItemsInStageViewlet): 
    name = _("scheduled")
    states = [
        agendaitem_wf_state[u"scheduled"].id,
        motion_wf_state[u"scheduled"].id,
        ] + \
        get_states("bill", tagged=["scheduled"]) + \
        get_states("question", keys=["scheduled"]) + \
        get_states("tableddocument", keys=["scheduled"])
    list_id = "items-scheduled"


class MinistryItemsViewlet(ViewletBase):
    list_id = "ministry-items"
    name = _("questions to the ministry")
    states = None
    response_types = ['O','W']
    
    def _getItems(self, ministry):
        session = Session()
        date_formatter = self.request.locale.dates.getFormatter('date', 'short')
        def _q_data_item(q):
            item = {}
            item['qid']= 'q_%s' % q.question_id
            if q.question_number:
                item['subject'] = u'Q %s %s (%s)' % (
                                    q.question_number, q.short_name, q.status)
            else:
                item['subject'] = u'%s (%s)' % (q.short_name, q.status)
            item['title'] = u'%s (%s)' % (q.short_name, q.status)
            item['result_item_class'] = 'workflow-state-%s' % q.status
            item['url'] = 'questions/obj-%s' % q.question_id
            item['status'] = misc.get_wf_state(q)
            item['status_date'] = date_formatter.format(q.status_date)
            item['owner'] = "%s %s" %(q.owner.first_name, q.owner.last_name)
            item['type'] = _(q.type)
            if type(q)==domain.Question:
                item['to'] = q.ministry.short_name
            else:
                item['to']= u""
            return item
        # prepare query for this ministry's questions
        mq_query = session.query(domain.Question).filter(sql.and_(
                domain.Question.ministry_id==ministry.group_id,
                domain.Question.status.in_(self.states),
                domain.Question.response_type.in_(self.response_types)
                ))
        return [ _q_data_item(question) for question in mq_query.all() ]
           
    def getData(self):
        """ template calls this to get the data of the query setup in update()
        """
        return [ item for ministry in self.query.all() 
                 for item in self._getItems(ministry) ]
    
    def update(self):
        """
        refresh the query
        """
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

class MinistryArchiveViewlet(MinistryItemsViewlet):
    name = _("archived items")
    # Ministry archive only includes Questions in a public terminal state
    states = get_states("question", 
                    tagged=["public", "terminal"], conjunction="AND")
    list_id = "items-archived"

class OralMinistryQuestionsViewlet(MinistryItemsViewlet):
    list_id = "ministry-oral-questions"
    name = _("oral questions")
    states = get_states("question", tagged=["oral"])
    response_types = ['O']

class WrittenMinistryQuestionsViewlet(MinistryItemsViewlet):
    list_id = "ministry-written-questions"
    name = _("written questions")
    states = get_states("question", tagged=["written"])
    response_types = ['W']

class InProgressMinistryItemsViewlet(MinistryItemsViewlet):
    """
    going through the workflow in clerks/speakers office
    """
    name = _("in progress")
    states = get_states("question", keys=["response_submitted"])
    list_id = "items-in-progress"

class DraftSittingsViewlet(viewlet.ViewletBase):
    render = ViewPageTemplateFile ('templates/workspace_sitting_viewlet.pt')
    
    name = _("agendas/minutes")
    states = [
        sitting_wf_state[u"draft-agenda"].id,
        sitting_wf_state[u"draft-minutes"].id,
    ]
    list_id = "sitting-draft"

    def getData(self):
        """
        return the data of the query
        """
        data_list = []
        results = self.query.all()
        formatter = self.request.locale.dates.getFormatter('date', 'short')
        for result in results:
            data ={}
            data['subject'] = result.short_name
            if ICommittee.providedBy(result.group):
                #http://localhost:8081/business/committees/obj-194/calendar/group/sittings/obj-5012/schedule
                data['url'] = 'committees/obj-%i/calendar/group/sittings/obj-%i/schedule' % (
                    result.group.group_id, result.sitting_id)
            else:
                #http://localhost:8081/calendar/group/sittings/obj-5011/schedule
                data['url'] = 'calendar/obj-%i/schedule' % result.sitting_id
            data['items'] = ''
            data['status'] = misc.get_wf_state(result)
            data['status_date'] = formatter.format(result.status_date)
            data['owner'] = ""
            data['type'] =  result.group.type
            data['group'] = u"%s %s" %(result.group.type.capitalize(), 
                result.group.short_name)
            data['date'] = u"%s %s" % (
                result.start_date.strftime('%Y-%m-%d %H:%M'), 
                #formatter.format(
                result.sitting_type.sitting_type)
            if type(result)==domain.Question:
                data['to'] = result.ministry.short_name
            else:
                data['to']= u""
            data_list.append(data)
        return data_list

    def update(self):
        """
        refresh the query
        """
        session = Session()
        qfilter = domain.GroupSitting.status.in_(self.states)
        sittings = session.query(domain.GroupSitting).filter(
                qfilter).order_by(domain.GroupSitting.start_date.desc()
                    ).options(
                eagerload('group'),
                eagerload('sitting_type')
                )
        self.query = sittings

