# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Form schema -- implementations of read-only derived attributes.

Signature of all utilities here: 

    (context:Object) -> any

$Id$
"""
log = __import__("logging").getLogger("bungeni_custom.forms")


# doc

def submission_date(context):
    return context._get_workflow_date("submitted")

def admissible_date(context):
    return context._get_workflow_date("admissible")

def gazetted_date(context):
    return context._get_workflow_date("gazetted")

def scheduled_date(context):
    return context._get_workflow_date("scheduled")

def response_pending_date(context):
    return context._get_workflow_date("response_pending")


