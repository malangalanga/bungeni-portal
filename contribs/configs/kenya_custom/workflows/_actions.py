# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Workflow transition-to-state actions.

Signature of all transition-to-state action callables:

    (context:Object) -> None

All transition-to-state actions are executed "on workflow trransition" i.e. 
exactly when the status is updated from the source to the destination state, 
and in exactly the order they are specified in the state.@actions xml attribute.

For more samples of source definitions of transition conditions, see the
following corresponding bungeni module:

    bungeni.core.workflows._actions

REMEMBER: when a transition-to-state action is executed, the context.status 
is already updated to the destination state.

$Id$
"""
log = __import__("logging").getLogger("bungeni_custom.workflows")

from bungeni.core.workflows._actions import (
    
    # all
    version, # context must be version-enabled
    
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

