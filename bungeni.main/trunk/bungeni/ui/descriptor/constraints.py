# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Field constraints and schema invariants

$Id$
"""
import re
import zope.schema
from zope.interface import Invalid
from bungeni.ui.i18n import _


# field constraints

EMAIL_RE = ("([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@"
    "(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)"
    "+[a-zA-Z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$"
)
LOGIN_RE = "^([a-zA-Z]){1}[a-zA-Z0-9_.]+$"

class FailedRegexMatch(zope.schema.ValidationError):
    """"Regex error initialized with a message displayed to user"""
    e_message = None

    def __init__(self, e_message=_(u"Invalid value"), *args, **kwargs):
        self.e_message = e_message
        super(FailedRegexMatch, self).__init__(*args, **kwargs)
    
    def doc(self):
        return self.e_message

class RegexChecker(object):
    """Regex constraint factory"""
    def __init__(self, regex, e_message):
        assert type(regex) in [str, unicode]
        self.regex = regex
        self.e_message = e_message
    
    def __call__(self, value):
        if type(value) in [str, unicode]:
            if re.match(self.regex, value) is None:
                raise FailedRegexMatch(self.e_message)
                return False
        return True

check_email = RegexChecker(EMAIL_RE, _(u"This is not a valid email address"))
check_login = RegexChecker(LOGIN_RE, _(u"Invalid login name"))


# schema invariants

def ElectionAfterStart(obj):
    """Start Date must be after Election Date."""
    if obj.election_date >= obj.start_date:
        raise Invalid(
            _("The life of a parliament must start after its election"),
            "election_date",
            "start_date"
        )

def EndAfterStart(obj):
    """End Date must be after Start Date."""
    if obj.end_date is None: return
    if obj.end_date <= obj.start_date:
        raise Invalid(
            _("End Date must be after Start Date"),
            "start_date",
            "end_date"
        )

''' !+UNUSED
def DissolutionAfterReinstatement(obj):
    """A committee must be disolved before it can be reinstated."""
    if (obj.dissolution_date is None) or (obj.reinstatement_date is None):
        return
    if obj.dissolution_date > obj.reinstatement_date:
        raise Invalid(
            _("A committee must be disolved before it can be reinstated"),
            "dissolution_date",
            "reinstatement_date"
        )
'''

def ActiveAndSubstituted(obj):
    """A person cannot be active and substituted at the same time."""
    if obj.active_p and obj.replaced_id:
        raise Invalid(
            _("A person cannot be active and substituted at the same time"),
            "active_p",
            "replaced_id"
        )

def SubstitudedEndDate(obj):
    """If a person is substituted he must have an end date."""
    if not obj.end_date and obj.replaced_id:
        raise Invalid(
            _("If a person is substituted End Date must be set"),
            "replaced_id",
            "end_date"
        )

def InactiveNoEndDate(obj):
    """If you set a person inactive you must provide an end date."""
    if not obj.active_p:
        if not (obj.end_date):
            raise Invalid(
                _("If a person is inactive End Date must be set"),
                "end_date",
                "active_p"
            )

def MpStartBeforeElection(obj):
    """MP start date (when set) must be after election."""
    if obj.election_nomination_date is None:
        return
    if obj.election_nomination_date > obj.start_date:
        raise Invalid(_("A parliament member has to be "
                "elected/nominated before she/he can be sworn in"),
            "election_nomination_date",
            "start_date"
        )

def DeathBeforeLife(user):
    """Check if date of death is after date of birth."""
    if user.date_of_death is None: return
    if user.date_of_death < User.date_of_birth:
        raise Invalid(_("Check dates: death must follow birth"),
            "date_of_death",
            "date_of_birth"
        )


