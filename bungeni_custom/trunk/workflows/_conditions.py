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
    
    # common
    # the condition for the creation transition from "" (None) to either 
    # "draft" or to "working_draft" seems to need the explicit condition (and 
    # negation of condition) on each of the two transition options 
    user_is_not_context_owner, 
    user_is_context_owner,
    # sub-instances
    user_may_edit_context_parent,
    # common global settings
    clerk_receive_notification,
    owner_receive_notification,
    ministry_receive_notification,
    
    # parliamentary items
    is_scheduled,
    
    # group
    # A group can only be dissolved if an end date is set.
    has_end_date,
    
    # groupsitting
    has_venue,
    has_agenda,
    agenda_finalized,
    
    # question
    is_written_response,
    is_oral_response,  
    response_allow_submit, # The "submit_response" workflow transition should 
    # NOT be displayed when the UI is displaying the question in "edit" mode 
    # (this transition will deny bungeni.Question.Edit to the Minister).
    
    # user
    has_date_of_death,
    not_has_date_of_death,

    # auditables
    user_is_state_creator,
    user_is_state_creator_and_owner,
    user_is_state_creator_not_owner,

    # signatories
    pi_has_signatories,
    pi_signatories_check,
    pi_allow_signature,
    signatory_auto_sign,
    signatory_manual_sign,
    pi_signature_period_expired,
    pi_allow_signature_actions,
    pi_unsign_signature,
)

