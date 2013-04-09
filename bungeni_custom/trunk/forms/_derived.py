# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Form schema -- implementations of read-only derived attributes.

Signature of all utilities here: 

    (context:Object) -> any

$Id$
"""
from bungeni.utils.misc import describe
from bungeni.ui.i18n import _
log = __import__("logging").getLogger("bungeni_custom.forms")


# doc

@describe(_(u"Submission Date"))
def submission_date(context):
    return context._get_workflow_date("submitted")


@describe(_(u"Admissible Date"))
def admissible_date(context):
    return context._get_workflow_date("admissible")


@describe(_(u"Gazetted Date"))
def gazetted_date(context):
    return context._get_workflow_date("gazetted")


@describe(_(u"Scheduled Date"))
def scheduled_date(context):
    return context._get_workflow_date("scheduled")


# user

@describe(_(u"Full Name : First name - middle name - last name"))
def user_combined_name(user):
    return " ".join([ name for name in 
            (user.first_name, user.middle_name, user.last_name) if name ])


# group

#!+i18n?
def group_combined_name(group):
    return "%s [%s]" % (group.full_name, group.acronym)


