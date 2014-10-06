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
    set_doc_registry_number, 
    set_doc_type_number,
    unschedule_doc, # !+ should be application logic
    propagate_parent_assigned_group_role,  # !+ should be application logic 
    
    # group
    activate, # set group role (grant via membership to all active members)
    deactivate, # unset group role (disable inheritance via membership for all members)
    dissolve, # end all memberships and child groups (and their memberships)
    
    # sitting
    schedule_sitting_items,
    
    # utility to help create parametrized "transfer to chamber" actions notes:
    # - sub-docs "signatories", "attachments", "events" are not carried over
    # - the "owner" of the new doc is the original owner i.e. the member of the
    #   originating chamber
    # PARAMETERS: (source_doc, target_chamber_type, target_type_key, target_state_id)
    # RETURNS the newly created doc (should anything need to be tweaked further on it)
    spawn_doc,
)
'''
def send_motion_to_senate(assembly_motion):
    """A sample action to "send" (spawn new) a document to other chamber.
    """
    # from {assembly_motion}, spawn a new doc of type "senate_motion", 
    # set its chamber to be the (expected singular) active "higher_house", 
    # and set the initial workflow state of the new doc to be "admissible".
    new_doc = spawn_doc(assembly_motion, "higher_house", "senate_motion", "admissible")
'''
def send_motion_to_senate(assembly_motion):
    d = spawn_doc(assembly_motion, "higher_house", "senate_motion", "admissible")

def send_motion_to_assembly(senate_motion):
    d = spawn_doc(senate_motion, "lower_house", "assembly_motion", "admissible")

def send_bill_to_senate(assembly_bill):
    d = spawn_doc(assembly_bill, "higher_house", "senate_bill", "reviewed")

def send_bill_to_assembly(senate_bill):
    d = spawn_doc(senate_bill, "lower_house", "assembly_bill", "reviewed")


