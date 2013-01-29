# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Workflow transition actions.

Signature of all action callables:

    (context:Object) -> None

All state transition actions are set ON execution of the workflow trransition 
i.e. the status has already been updated to destination state id. 

The order of execution of any actions follows same order of how actions are 
listed in state.@actions xml attribute.

The specially-handled "version" action, specified via state.@version="true",
whenever present is ALWAYS executed as first action.
!+ drop @version bool attr for simply another action?

For more samples of source definitions of transition conditions, see the
following corresponding bungeni module:

    bungeni.core.workflows._actions

$Id$
"""
log = __import__("logging").getLogger("bungeni_custom.workflows")

from bungeni.core.workflows._actions import (
    
    # version
    create_version as version,
    
    # doc
    set_doc_registry_number, # when a doc is received
    set_doc_type_number, # when a doc is admitted
    unschedule_doc, # when a doc is withdrawn
    
    # queston !+CUSTOM
    assign_role_minister_question,
    
    # group
    activate,
    dissolve,
    
    # sitting
    set_real_order,
    schedule_sitting_items,
    
    # user
    assign_owner_role,

)

