# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Form validations for custom forms

$Id$

Validators API:
    validator(action, data, context, container) -> [error]
# !+ADD actions means context is categorically None
"""
log = __import__("logging").getLogger("bungeni.ui.forms.validations")

import datetime

from zope.security import checkPermission
from zope.security.proxy import removeSecurityProxy
from zope.interface import Invalid

import sqlalchemy as rdb
from bungeni.alchemist import Session
from bungeni.models import interfaces
from bungeni.models import schema
from bungeni.models import venue
from bungeni.models import domain
from bungeni.ui.i18n import _
from bungeni.ui.utils import queries
from bungeni.ui.calendar.utils import generate_dates
from bungeni.ui.calendar.utils import datetimedict
from interfaces import Modified

from bungeni.utils.capi import capi

# utils

def logged_errors(errors, vname, logger=log.debug):
    if errors:
        logger("\n        ".join(
                [" %s FAILS ->" % (vname)] + [str(e) for e in errors]))
    return errors


def null_validator(*args, **kwargs):
    return []

def as_date(date):
    """(date:either(datetime.datetime, datetime.date)) -> dateime.date
    """
    if isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, datetime.date):
        return date
    else:
        raise TypeError(_("invalid date. choose or type correct date"))


# validators

def email_validator(action, data, context, container):
    session = Session()
    users = session.query(domain.User
        ).filter(domain.User.email==data.get("email", ""))
    if users.count() > 1:
        return [Invalid(_(u"Email already taken!"), "email")]
    if context:
        if users.count() == 1 and users.first().user_id != context.user_id:
            return [Invalid(_(u"Email already taken!"), "email")]
    elif users.count() > 0:
        return [Invalid(_(u"Email already taken!"), "email")]
    return []


def validate_start_date_within_parent(parent, data):
    """Check that the start date is inside the restrictictions.
    It must not start before the contextParents start date or end
    after the contextsParents end date"""
    errors = []
    start_date = data.get("start_date")
    if start_date:
        start = as_date(start_date)
        if getattr(parent, "start_date", None):
            pstart = as_date(parent.start_date)
            if start < pstart:
                errors.append(Invalid(
                        _(u"Start date must be after (%s)") % pstart, 
                        "start_date"))
        if getattr(parent, "end_date", None):
            pend = as_date(parent.end_date)
            if start > pend:
                errors.append(Invalid(
                        _(u"Start date must be prior to (%s)") % pend, 
                        "start_date"))
    return logged_errors(errors, "validate_start_date_within_parent")


def validate_start_date_equals_end_date(action, data, context, container):
    """Check that the start date and end date fall within the same day."""
    errors = []
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if start_date and end_date:
        start = as_date(start_date) 
        end = as_date(end_date)
        if (start != end) and (not data.get("rec_type")):
            errors.append(Invalid(
                    _(u"End date must be equal to start date"),
                    "end_date"))

    return logged_errors(errors, "validate_start_date_equals_end_date")


def validate_end_date_within_parent(parent, data):
    """Check that the end date is inside the restrictictions.
    It must not end before the context.Parents start date or end
    after the context.Parents end date
    """
    errors = []
    end_date = data.get("end_date")
    if end_date:
        end = as_date(end_date)
        if getattr(parent, "start_date", None):
            pstart = as_date(parent.start_date)
            if end < pstart:
                errors.append(Invalid(
                        _(u"End date must be after (%s)") % pstart, 
                        "end_date"))
        if getattr(parent, "end_date", None):
            pend = as_date(parent.end_date)
            if end > pend:
                errors.append(Invalid(
                        _(u"End date must be prior to (%s)") % pend, 
                        "end_date"))
    return logged_errors(errors, "validate_end_date_within_parent")


def validate_date_range_within_parent(action, data, context, container):
    errors = validate_start_date_within_parent(container.__parent__, data)
    errors = errors + validate_end_date_within_parent(container.__parent__, data)
    return logged_errors(errors, "validate_date_range_within_parent")

class AllPoliticalGroupMemberships(object):
    """Helper class to get all political_group memberships for all users.
    """

all_political_group_memberships = rdb.join(
    schema.user_group_membership, schema.group).join(schema.political_group)
        
rdb.orm.mapper(AllPoliticalGroupMemberships, all_political_group_memberships)

def validate_political_group_membership(action, data, context, container):
    errors = []
    parent_id = getattr(container.__parent__, "parent_group_id", None)
    user_id = data.get("user_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if interfaces.IPoliticalGroupMember.providedBy(context):
        political_group_member = context
        user_id = context.user_id
    else:
        political_group_member = None
    if start_date:
        for r in queries.validate_membership_in_interval(political_group_member, 
                    AllPoliticalGroupMemberships, 
                    start_date,
                    user_id,
                    parent_id=parent_id,
                    with_parent=True):
            overlaps = r.short_name
            errors.append(Invalid(
                    _("The person is a member in (%s) at that date") % overlaps, 
                    "start_date"))
    if end_date:
        for r in queries.validate_membership_in_interval(political_group_member, 
                    AllPoliticalGroupMemberships, 
                    end_date,
                    user_id,
                    parent_id=parent_id,
                    with_parent=True):
            overlaps = r.short_name
            errors.append(Invalid(
                    _("The person is a member in (%s) at that date") % overlaps, 
                    "end_date"))
    for r in queries.validate_open_membership(political_group_member, 
            AllPoliticalGroupMemberships, 
            user_id, 
            parent_id=parent_id, 
            with_parent=True):
        overlaps = r.short_name
        errors.append(Invalid(
                _("The person is a member in (%s) at that date") % overlaps, 
                "end_date")) 
    return logged_errors(errors, "validate_political_group_membership")


def validate_parliament_dates(action, data, context, container):
    """Parliaments must not overlap."""
    errors = []
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    election_date = data.get("election_date")
    if interfaces.IParliament.providedBy(context):
        parliament = context
    else:
        parliament = None
    if start_date:
        results = queries.validate_date_in_interval(parliament, 
            domain.Parliament,  start_date)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                _("The start date overlaps with (%s)") % overlaps, "start_date"
            ))
    if end_date:
        results = queries.validate_date_in_interval(parliament, 
            domain.Parliament, end_date)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                    _("The end date overlaps with (%s)") % overlaps, "end_date"
            ))
    if election_date:
        results = queries.validate_date_in_interval(parliament, 
            domain.Parliament, election_date)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                _("The election date overlaps with (%s)") % overlaps, 
                "election_date"))
    if parliament is None:
        results = queries.validate_open_interval(parliament, domain.Parliament)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                    _("Another parliament is not yet dissolved (%s)") % overlaps,
                    "election_date"))
    return logged_errors(errors, "validate_parliament_dates")

def validate_government_dates(action, data, context, container):
    errors = []
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if interfaces.IGovernment.providedBy(context):
        government = context
    else:
        government = None
    if container.__parent__.end_date is not None and start_date:
        if start_date > container.__parent__.end_date:
            errors.append(Invalid(
                    "%s %s" % (_("Start date cannot be after the parliaments"
                            " dissolution"), container.__parent__.end_date), 
                    "start_date"))
    if start_date and container.__parent__.start_date > start_date:
        errors.append(Invalid(
                "%s %s" % (
                    _("Start date must start after the swearing in of the"
                        " parliament"), container.__parent__.start_date), 
                "start_date"))
    if start_date:
        results = queries.validate_date_in_interval(government, 
            domain.Government, start_date)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                    _("The start date overlaps with (%s)") % overlaps, 
                    "start_date"))
    if end_date:
        results = queries.validate_date_in_interval(government, 
                    domain.Government, end_date)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                    _("The end date overlaps with (%s)") % overlaps, 
                    "end_date"))
    if government is None:
        results = queries.validate_open_interval(government, domain.Government)
        for result in results:
            overlaps = result.short_name
            errors.append(Invalid(
                    _("Another government is not yet dissolved (%s)") % overlaps,
                    "start_date"))
        
    return logged_errors(errors, "validate_government_dates")


def validate_group_membership_dates(action, data, context, container):
    """A User must be member of a group only once at a time.
    """
    group_id = container.__parent__.group_id
    user_id = data.get("user_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    # !+ADD actions means context is categorically None 
    if interfaces.IBungeniGroupMembership.providedBy(context):
        group_membership = context
    else:
        group_membership = None
    #!+IMPROVE(murithi, apr-2011) VALIDATION
    if user_id is None:
        return []
    errors = []
    if start_date:
        for r in queries.validate_membership_in_interval(group_membership, 
                    domain.GroupMembership, 
                    start_date,
                    user_id, group_id):
            overlaps = r.group.short_name
            errors.append(Invalid(
                    _("The person is a member in (%s) at that date") % overlaps, 
                    "start_date", "user_id"))
    if end_date:
        for r in queries.validate_membership_in_interval(group_membership, 
                    domain.GroupMembership, 
                    end_date,
                    user_id, group_id):
            overlaps = r.group.short_name
            errors.append(Invalid(
                    _("The person is a member in (%s) at that date") % overlaps, 
                    "end_date", "user_id"))
    for r in queries.validate_open_membership(group_membership, 
                domain.GroupMembership, 
                user_id, group_id):
        overlaps = r.group.short_name
        errors.append(Invalid(
                    _("The person is a member in (%s) at that date") % overlaps, 
                    "end_date", "user_id"))
    return logged_errors(errors, "validate_group_membership_dates")
                 

class GroupMemberTitle(object):
    """ Titels that may be held by multiple persons of the
    group at the same time"""

group_member_title = rdb.join(schema.user_group_membership, 
        schema.member_title).join(
            schema.title_type)

rdb.orm.mapper(GroupMemberTitle, group_member_title)


def validate_member_titles(action, data, context, container):
    """Titles for members follow the restrictions:
    A person must have the same title only once (e.g. you cannot
    be chairperson in a group twice at a time)
    If a Title is unique (e.g. chairperson) there can be only one person 
    at a time in this group holding this title, other titles like member 
    may be applied to several persons at the same time""" 
    def get_q_user(date):
        return session.query(GroupMemberTitle).filter(
                rdb.and_(
                    schema.user_group_membership.c.group_id == group_id,
                    schema.user_group_membership.c.membership_id == membership_id,
                    schema.member_title.c.title_type_id == title_type_id,
                    rdb.or_(
                        rdb.between(
                            date, 
                            schema.member_title.c.start_date,
                            schema.member_title.c.end_date),
                        schema.member_title.c.end_date == None
                    )))
    def get_q_unique(date):
        return session.query(GroupMemberTitle).filter(
            rdb.and_(
                schema.user_group_membership.c.group_id == group_id,
                schema.title_type.c.user_unique == True,
                schema.member_title.c.title_type_id == title_type_id,
                rdb.or_(
                    rdb.between(
                        date, 
                        schema.member_title.c.start_date,
                        schema.member_title.c.end_date),
                    schema.member_title.c.end_date == None
                )))
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    errors = []
    group_id = container.__parent__.group_id
    membership_id = container.__parent__.membership_id
    session = Session()
    title_type_id = data.get("title_type_id")
    if interfaces.IMemberTitle.providedBy(context):
        title = context
    else:
        title = None
    if  start_date:
        q = get_q_user(start_date)
        results = q.all()
        for result in results:
            overlaps = result.title_name
            if title:
                if title.member_title_id == result.member_title_id:
                    continue
                else:
                    errors.append(Invalid(
                            _(u"This persons already has the title %s") % (
                                overlaps), 
                            "start_date"))
            else:
                errors.append(Invalid(
                        _(u"This persons already has the title %s") % (
                            overlaps), 
                        "start_date")) 
    if end_date:
        q = get_q_user(end_date)
        results = q.all()
        for result in results:
            overlaps = result.title_name
            if title:
                if title.member_title_id == result.member_title_id:
                    continue
                else:
                    errors.append(Invalid(
                            _(u"This persons already has the title %s") % (
                                overlaps),
                            "end_date"))
            else:
                errors.append(Invalid(
                        _(u"This persons already has the title %s") % (
                            overlaps), 
                        "end_date"))
    if start_date:
        q = get_q_unique(start_date)
        results = q.all()
        for result in results:
            overlaps = result.title_name
            if title:
                if title.member_title_id == result.member_title_id:
                    continue
                else:
                    errors.append(Invalid(
                            _(u"A person with the title %s already exists") % (
                                overlaps), 
                            "start_date"))
            else:
                errors.append(Invalid(
                        _(u"A person with the title %s already exists") % (
                            overlaps),
                        "start_date"))
    if end_date:
        q = get_q_unique(end_date)
        results = q.all()
        for result in results:
            overlaps = result.title_name
            if title:
                if title.member_title_id == result.member_title_id:
                    continue
                else:
                    errors.append(Invalid(
                            _(u"A person with the title %s already exists") % (
                                overlaps),
                            "end_date"))
            else:
                errors.append(Invalid(
                        _(u"A person with the title %s already exists") % (
                            overlaps),
                        "end_date"))
    return logged_errors(errors, "validate_member_titles")

def validate_venues(action, data, context, container):
    """A venue can only be booked for one sitting at once."""
    errors = []
    start = data.get("start_date")
    #check if this is an update to a recurring event(ignore venue check)
    if action.form.request.get("rec_type") != None:
        return []
    end = data.get("end_date")
    if interfaces.ISitting.providedBy(context):
        sitting = context
    else:
        sitting = None
    venue_id = data.get("venue_id")
    if venue_id is not None:
        venue_id = long(venue_id)
        session = Session()
        svenue = session.query(domain.Venue).get(venue_id)
    else:
        return []
    if not(start and end):
        return []
    for booking in  venue.check_venue_bookings(start, end, svenue, sitting):
        errors.append(
            Invalid(
                    _(u'Venue "$venue" already booked in this time slot',
                        mapping={"venue": booking.short_name}),
                    "venue_id"))
    return logged_errors(errors, "validate_venues")

def validate_recurring_sittings(action, data, context, container):
    """Validate recurring sittings.

    This validator determines the sittings that will be created and
    confirms the validity of them.
    """

    start = data.get("start_date")
    end = data.get("end_date")
    weekdays = data.get("weekdays")
    monthly = data.get("monthly")
    repeat = data.get("repeat")
    repeat_until = data.get("repeat_until")
    exceptions = data.get("exceptions", ())
    
    session = Session()
    group_id = container.__parent__.group_id
    group = session.query(domain.Group).get(group_id)
    
    errors = []
    if weekdays or monthly:
        # this should be an invariant, but due to formlib's requirement
        # that invariant methods pertain to a single schema, it's not
        # possible
        if repeat_until is not None and repeat_until < start.date():
            #session.close()
            return [Invalid(
                _(u"If recurrence is limited by date, it "
                  "must lie after the starting date"),
                "repeat_until")]

        # verify that dates do not violate group's end date
        for date in generate_recurring_sitting_dates(
            start.date(), repeat, repeat_until, weekdays, monthly, exceptions):
            if group.end_date is not None and date > group.end_date:
                errors.append(Invalid(
                        _(u"One or more events would be scheduled for $F, which is "
                            "after the scheduling group's end date",
                            mapping={"F":datetimedict.fromdate(date)}),
                        "repeat" if repeat else "repeat_until"))
                break
            event_data = {
                "start_date": datetime.datetime(
                    date.year, date.month, date.day, start.hour, start.minute),
                "end_date": datetime.datetime(
                    date.year, date.month, date.day, end.hour, end.minute),
                }
            errors.extend(validate_non_overlapping_sitting(
                action, event_data, context, container,
                "weekdays" if weekdays else "monthly"))
            if errors:
                break
            errors.extend(validate_venues(
                action, data, context, container))
            if errors:
                break
    return logged_errors(errors, "validate_recurring_sittings")

def validate_non_overlapping_sitting(action, data, context, container, *fields):
    start = data.get("start_date")
    end = data.get("end_date")
    if not fields:
        fields = "start_date", "end_date"
    session = Session()
    group_id = container.__parent__.group_id
    group = session.query(domain.Group).get(group_id)
    sittings = group.sittings

    for sitting in queries.get_sittings_between(sittings, start, end):
        if context != sitting:
            return logged_errors(
                [Invalid(
                    _(u"One or more events would be scheduled for $F, which "
                        "overlaps with an existing sitting",
                        mapping={"F":datetimedict.fromdatetime(start)}),
                *fields)],
                "validate_non_overlapping_sitting")
    return []


def generate_recurring_sitting_dates(start_date, repeat, repeat_until,
                                     weekdays, monthly, exceptions):
    if repeat_until is not None:
        assert repeat_until > start_date
    generators = []
    if weekdays is not None:
        for weekday in weekdays:
            generators.append(iter(weekday(start_date)))
    if monthly is not None:
        generators.append(iter(monthly(start_date)))
    count = 0
    for date in generate_dates(*generators):
        if date in exceptions:
            continue
        count += 1
        if repeat and count > repeat:
            break
        if repeat_until and date.date() > repeat_until:
            break
        yield date.date()

def validate_sub_role_unique(action, data, context, container):
    errors = []
    sub_role_id = data.get("role_id")
    if sub_role_id:
        group_id = container.__parent__.group_id
        session = Session()
        title_types = session.query(domain.TitleType
            ).filter(schema.title_type.c.group_id==group_id).all()
        if sub_role_id in [title_type.role_id for title_type in title_types]:
            errors.append(Invalid(
                        _(u"A title with %s sub role already exists") % (
                            sub_role_id)))
    return logged_errors(errors, "validate_sub_role_unique")

def diff_validator(form, context, data):
    """Custom validator that checks if form timestamp differs from timestamp in db.
    Returns list of Modified errors for fields which differs from db values.
    """
    diff = form.request.form.get("diff", "")
    errors = []
    last_timestamp = form.request.form.get("last_timestamp", "")
    context = removeSecurityProxy(context)    
    current_timestamp = str(data.get("timestamp", ""))
    db_timestamp = str(context.timestamp)
    # if we're in diff mode we don't care if form.timestamp equals db timestamp    
    if (current_timestamp != db_timestamp and diff!="True") or\
       (last_timestamp!=db_timestamp and last_timestamp):
            for name, value in data.items():
                if context.__dict__[name] != value:
                    errors.append(Modified(_(u"Value was changed!"), name))
    return logged_errors(errors, "diff_validator")

