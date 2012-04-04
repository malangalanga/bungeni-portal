# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Worklfow utilities

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.workflows.utils")

import sys
import datetime

from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.app.component.hooks import getSite
from bungeni.core.workflow.interfaces import IWorkflowController, IWorkflow
from bungeni.core.workflow.interfaces import (NoTransitionAvailableError, 
    InvalidStateError
)

import bungeni.models.interfaces as interfaces
#import bungeni.models.domain as domain
import bungeni.models.utils
import bungeni.core.version
#import bungeni.core.globalsettings as prefs
from bungeni.ui.utils import debug

import re
import dbutils

from bungeni.utils.capi import capi, bungeni_custom_errors

from ConfigParser import ConfigParser, NoOptionError
import os

SIGNATORIES_REJECT_STATES = [u"rejected", u"withdrawn"]

''' !+UNUSED(mr, mar-2011)
def get_parliament(context):
    """go up until we find a parliament """
    parent = context.__parent__
    while parent:
        if  interfaces.IParliament.providedBy(parent):
            return parent
        else:
            try:
                parent = parent.__parent__
            except:
                parent = None
    if not parent:
        parliament_id = context.parliament_id
        session = Session()
        parliament = session.query(domain.Parliament).get(parliament_id)
        return parliament
'''


get_principal_id = bungeni.models.utils.get_principal_id

def formatted_user_email(user):
    return '"%s %s" <%s>' % (user.first_name, user.last_name, user.email)

# parliamentary item

def get_owner_pi(context):
    """Get the user who has been previously set as the owner of this item 
    (must support IOwned i.e. ParliamentaryItem or Attachment).
    """
    assert interfaces.IOwned.providedBy(context), \
        "Not an Owned (parliamentary) Item: %s" % (context)
    return dbutils.get_user(context.owner_id)

def get_owner_login_pi(context):
    """Get the login of the user who is the owner of this item.
    #!+ CLEANOUT, just use get_owner_pi(context).login directly
    """
    return get_owner_pi(context).login

def assign_owner_role(context, login):
    # throws IntegrityError when login is None
    IPrincipalRoleMap(context).assignRoleToPrincipal("bungeni.Owner", login)

def assign_owner_role_pi(context):
    """Assign bungeni.Owner role to the ParliamentaryItem.
    """
    current_user_login = get_principal_id()
    owner_login = get_owner_login_pi(context)
    log.debug("assign_owner_role_pi [%s] user:%s owner:%s" % (
        context, current_user_login, owner_login))
    if current_user_login:
        assign_owner_role(context, current_user_login)
    if owner_login and (owner_login != current_user_login):
        assign_owner_role(context, owner_login)

def create_version(context):
    """Create a new version of an object and return it.
    Note: context.status is already updated to destination state.
    """
    # !+capi.template_message_version_transition
    message_template = "New version on workflow transition to: %(status)s"
    message = message_template % context.__dict__
    return bungeni.core.version.create_version(context, message, manual=False)


@bungeni_custom_errors
def get_mask(context):
    # assert IBungeniParliamentaryContent.providedBy(context)
    # !+IBungeniParliamentaryContent(mr, nov-2011) only context typed
    # interfaces.IBungeniParliamentaryContent should ever get here!
    # But for this case, all we need is that context defines a type:
    m = "PI context [%s] for get_mask must specify a type attr" % (context)
    assert hasattr(context, "type"), m
    path = capi.get_path_for("registry")
    config = ConfigParser()
    config.readfp(open(os.path.join(path, "config.ini")))
    try:
        return config.get("types", context.type)
    except NoOptionError:
        return None


def set_pi_registry_number(context):
    """A parliamentary_item's registry_number should be set on the item being 
    submitted to parliament.
    """
    mask = get_mask(context)
    if mask == "manual" or mask is None:
        return
    
    items = re.findall(r"\{(\w+)\}", mask)
    
    for name in items:
        if name == "registry_number":
            mask = mask.replace("{%s}" % name, str(dbutils.get_next_reg()))
            continue
        if name == "progressive_number":
            mask = mask.replace("{%s}" % name, 
                                         str(dbutils.get_next_prog(context)))
            continue
        value = getattr(context, name)
        mask = mask.replace("{%s}" % name, value)
    
    if context.registry_number == None:
        dbutils.set_pi_registry_number(context, mask)

is_pi_scheduled = dbutils.is_pi_scheduled


# question
def setMinistrySubmissionDate(context):
    if context.ministry_submit_date == None:
        context.ministry_submit_date = datetime.date.today()

def assign_question_minister_role(context):
    assert interfaces.IQuestion.providedBy(context), \
        "Not a Question: %s" % (context)
    if context.ministry is not None:
        ministry_login_id = context.ministry.group_principal_id
        if ministry_login_id:
            IPrincipalRoleMap(context).assignRoleToPrincipal("bungeni.Minister", 
                ministry_login_id)

# !+QuestionScheduleHistory(mr, mar-2011) rename appropriately e.g. "unschedule"
# !+QuestionScheduleHistory(mr, mar-2011) only pertinent if question is 
# transiting from a shceduled state... is this needed anyway?
def setQuestionScheduleHistory(context):
    question_id = context.question_id
    dbutils.removeQuestionFromItemSchedule(question_id)

''' !+UNUSUED (and incorrect) :
def getQuestionSchedule(context):
    question_id = context.question_id
    return dbutils.is_pi_scheduled(question_id)

def getMotionSchedule(context):
    motion_id = context.motion_id
    return dbutils.is_pi_scheduled(motion_id)

def getQuestionSubmissionAllowed(context):
    return prefs.getQuestionSubmissionAllowed()
'''

# bill
def setBillPublicationDate(context):
    if context.publication_date == None:
        context.publication_date = datetime.date.today()

'''
# question, motion, bill, agendaitem, tableddocument
# !+setParliamentId(mr, mar-2011) this is used in "create" transitions... 
def setParliamentId(context):
    if not context.parliament_id:
         context.parliament_id = prefs.getCurrentParliamentId()
'''

# tableddocument
def setTabledDocumentHistory(context):
    pass

def get_group_local_role(group):
    if interfaces.IParliament.providedBy(group):
        return "bungeni.MP"
    elif interfaces.IMinistry.providedBy(group):
        return "bungeni.Minister"
    elif interfaces.ICommittee.providedBy(group): 
        return "bungeni.CommitteeMember"
    elif interfaces.IPoliticalGroup.providedBy(group):
        return "bungeni.PartyMember"
    elif interfaces.IGovernment.providedBy(group):
        return "bungeni.Government"
    elif interfaces.IOffice.providedBy(group):
        return group.office_role
    else:
        return "bungeni.GroupMember"

def get_group_context(context):
    if interfaces.IOffice.providedBy(context):
        return getSite() #get_parliament(context)
    else:
        return context

# groups
def _set_group_local_role(context, unset=False):
    group = context
    role = get_group_local_role(group)
    prm = IPrincipalRoleMap(get_group_context(group))
    if not unset:
        prm.assignRoleToPrincipal(role, group.group_principal_id)
    else:
        prm.unsetRoleForPrincipal(role, group.group_principal_id)
    
def set_group_local_role(context):
    _set_group_local_role(context, unset=False)
            
def unset_group_local_role(context):
    _set_group_local_role(context, unset=True)

def dissolveChildGroups(groups, context):
    for group in groups:
        IWorkflowController(group).fireTransition("active-dissolved", 
            check_security=False)
        
# groupsitting
def schedule_sitting_items(context):
    
    # !+fireTransitionToward(mr, dec-2010) sequence of fireTransitionToward 
    # calls was introduced in r5818, 28-jan-2010 -- here the code is reworked
    # to be somewhat more sane, and added logging of both SUCCESS and of 
    # FAILURE of each call to fireTransitionToward().
    #
    # The check/logging should be removed once it is understood whether
    # NoTransitionAvailableError is *always* raised (i.e. fireTransitionToward is
    # broken) or it is indeed raised correctly when it should be.
    
    def fireTransitionScheduled(item, check_security=False):
        try:
            IWorkflowController(item).fireTransitionToward("scheduled", 
                    check_security=False)
            raise RuntimeWarning(
                """It has WORKED !!! fireTransitionToward("scheduled")""")
        except (NoTransitionAvailableError, RuntimeWarning):
            debug.log_exc_info(sys.exc_info(), log.error)
    
    for schedule in context.item_schedule:
        wf = IWorkflow(schedule.item, None)
        if wf is None: 
            continue
        try:
            if wf.get_state("scheduled"):
                fireTransitionScheduled(schedule.item)
        except InvalidStateError:
            pass

def check_agenda_finalized(context):
    unfinalized_tags = ["tobescheduled", "scheduled"]
    def check_finalized(schedule):
        wfc = IWorkflowController(schedule.item, None)
        if wfc is None:
            return True
        #!+TYPES(mb, march-2012) There might be a more elegant approach here
        # to filter out 'text records' from the schedule
        if interfaces.IBungeniParliamentaryContent.providedBy(schedule.item):
            wfc, wfc.state_controller.get_status(),
            wfc.workflow.get_state_ids(not_tagged=unfinalized_tags,
                restrict=False
            )
            return (wfc.state_controller.get_status() in 
                wfc.workflow.get_state_ids(not_tagged=unfinalized_tags,
                    restrict=False
                )
            )
        else:
            return True
    check_list = map(check_finalized, context.items.values())
    return  (False not in check_list)

#signatories
def assign_signatory_role(context, owner_login, unset=False):
    log.debug("assign signatory role [%s] user: [%s]",
        context, owner_login
    )
    if unset:
        IPrincipalRoleMap(context).unsetRoleForPrincipal(
            u"bungeni.Signatory", owner_login
        )
    else:
        IPrincipalRoleMap(context).assignRoleToPrincipal(u"bungeni.Signatory", 
            owner_login
        )

def pi_update_signatories(context):
    """fire automatic transitions on submission of document"""
    for signatory in context.signatories.values():
        wfc = IWorkflowController(signatory, None)
        if wfc is not None:
            wfc.fireAutomatic()

def pi_unset_signatory_roles(context, all=False):
    """Unset signatory roles for members who have rejected document
    """
    if all:
        for signatory in context.signatories.values():
            owner_login = get_owner_login_pi(signatory)
            assign_signatory_role(context, owner_login, unset=True)
    else:
        for signatory in context.signatories.values():
            wfc = IWorkflowController(signatory, None)
            if wfc is not None:
                if (wfc.state_controller.get_status() 
                        in SIGNATORIES_REJECT_STATES
                    ):
                    owner_login = get_owner_login_pi(signatory)
                    log.debug("Removing signatory role for [%s] on "
                        "document: [%s]", 
                        owner_login, signatory.item
                    )
                    assign_signatory_role(context, owner_login, unset=True)
            else:
                log.debug("Unable to get workflow controller for : %s", signatory)

