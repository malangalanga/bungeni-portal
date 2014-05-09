# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Form schema -- implementations of read-only derived attributes.

Signature of all utilities here: 

    (context:domain.Entity) -> any

$Id$
"""
log = __import__("logging").getLogger("bungeni_custom.forms")


from bungeni.core.translation import translated
from bungeni.utils.misc import describe
from bungeni import _



# derived fields based on doc workflow dates -- see:
# models.domain.Doc._get_workflow_date


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



# derived fields by combining values from other fields - recommendation 
# is to use python's str.format functionalities, see:
# http://docs.python.org/2/library/string.html#formatexamples
# !+ from py 2.7, may do simply {} (without the number)

# user

@describe(_(u"Full Name : First name - middle name - last name"))
def user_combined_name(user):
    return u"{0} {1} {2}".format(
            user.first_name, 
            user.middle_name or "", # may be None
            user.last_name,
        ).replace("  ", " ")


# group

def group_combined_name(group):
    group = translated(group)
    return u"{0} [{1}]".format(
            group.full_name,
            group.acronym
        ).replace("  ", " ")


