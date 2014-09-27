# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Workflow transition (custom) conditions.

Signature of all utilities here: 

    (context:Object) -> bool
    
For samples of source definitions of transition conditions, see the following 
corresponding bungeni module:

    bungeni.core.workflows._conditions

$Id$
"""
log = __import__("logging").getLogger("bungeni_custom.workflows")

from bungeni.core.workflows._conditions import (
    
    # doc
    is_scheduled,
    
    # group
    # A group can only be dissolved if an end date is set.
    has_end_date,
    
    # groupsitting
    has_venue,
    has_agenda,
    agenda_finalized,
    sitting_dummy,
    
    # user
    has_date_of_death,
    not_has_date_of_death,
    
    # child items
    # A doc is a draft iff its current current state is tagged with "draft".
    context_parent_is_draft, 
    context_parent_is_not_draft,
    context_parent_is_public,
    context_parent_is_not_public,
    user_may_edit_context_parent,
    
    # signatory
    signatory_auto_sign,
    signatory_manual_sign,
    signatory_allowed_sign,
    signatory_allowed_actions,
    signatory_period_elapsed,
    signatory_allows_unsign,
    doc_has_signatories,
    doc_valid_num_consented_signatories,
    
)


# condition building-block utilities
from bungeni.core.workflows._conditions import (

    # get child document of specified type
    child, # (context, type_key) -> child
    
    # is context status one of the ones in state_ids?
    in_state, # (context, state_id, state_id, ...) -> bool
    
    # Is the context child document, identified by type_key, in one of the 
    # specified state_ids?
    child_in_state, # (context, type_key, state_id, state_id, ...) -> bool
)


# question

def is_written_response(question):
    """question: Require a written response.
    """
    return question.response_type == "written"

def is_oral_response(question):
    """question: Require an oral response.
    """
    return question.response_type == "oral"

def is_group_assigned(question):
    """question: Require that the question (normally with a written response) 
    has been assigned to exactly one group.
    """
    if question.group_assignment_feature.enabled:
        # must be assigned to exactly one group of a given type e.g. ministry !+?
        return len(question.group_assignments) == 1
    return False

def is_oral_response_or_is_group_assigned(question):
    """question: ok if question is oral response, else require that 
    it has been assigned to a group.
    """
    return is_oral_response(question) or is_group_assigned(question)

def is_written_response_and_is_group_assigned(question):
    """question: ok if question is written response and assigned to a group.
    """
    return is_written_response(question) and is_group_assigned(question)


def response_allow_submit_assembly(question):
    """question: Require that the event response has been completed.
    """
    return child_in_state(question, "assembly_event_response", "completed")

def response_allow_submit_senate(question):
    """question: Require that the event response has been completed.
    """
    return child_in_state(question, "senate_event_response", "completed")

def response_allow_publish_assembly(question):
    """question: Require that the event response has been reviewed.
    """
    return child_in_state(question, "assembly_event_response", "reviewed")

def response_allow_publish_senate(question):
    """question: Require that the event response has been reviewed.
    """
    return child_in_state(question, "senate_event_response", "reviewed")


''' !+composite_condition(mr, may-2012) ability to do this in xml directly?
def may_edit_context_parent_and_is_not_public(context):
    """A composite condition, combines two conditions."""
    return (
        user_may_edit_context_parent(context) and 
        context_parent_is_not_public(context))
'''

