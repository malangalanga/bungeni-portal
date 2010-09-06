#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni object domain

Created by Kapil Thangavelu on 2007-11-22.

$Id$
"""
log = __import__("logging").getLogger("bungeni.models.domain")

import md5, random, string

from zope import interface, location, component
from ore.alchemist import model, Session
from alchemist.traversal.managed import one2many
from zope.location.interfaces import ILocation
import sqlalchemy.sql.expression as sql

import interfaces

#

def object_hierarchy_type(object):
    if isinstance(object, User):
        return "user"
    if isinstance(object, Group):
        return "group"
    if isinstance(object, ParliamentaryItem):
        return "item"
    return ""


class Entity(object):

    interface.implements(location.ILocation)

    __name__ = None
    __parent__ = None

    def __init__(self, **kw):
        try:
            domain_schema = model.queryModelInterface(self.__class__)
            known_names = [k for k, d in domain_schema.namesAndDescriptions(1)]
        except:
            known_names = None

        for k, v in kw.items():
            if known_names is None or k in known_names:
                setattr(self, k, v)
            else:
                log.warn(
                    "Invalid attribute on %s %s" % (
                        self.__class__.__name__, k))

# sort_on is the column the query is sorted on by default
# sort_replace is a dictionary that maps one column to another
# so when the key is requested in a sort the value gets sorted
# eg: {'user_id':'sort_name'} when the sort on user_id is requested the 
# query gets sorted by sort_name
#

class User(Entity):
    """Domain Object For A User.
    General representation of a person
    """

    interface.implements(interfaces.IBungeniUser, interfaces.ITranslatable)

    def __init__(self, login=None, **kw):
        if login:
            self.login = login
        super(User, self).__init__(**kw)
        self.salt = self._makeSalt()

    def _makeSalt(self):
        return ''.join(random.sample(string.letters[:52], 12))

    def setPassword(self, password):
        self.password = self.encode(password)

    def getPassword(self):
        return None

    def encode(self, password):
        return md5.md5(password + self.salt).hexdigest()

    def checkPassword(self, password_attempt):
        attempt = self.encode(password_attempt)
        return attempt == self.password

    def _get_status(self):
        return self.active_p
    def _set_status(self, value):
        self.active_p = value
    status = property(_get_status, _set_status)

    @property
    def fullname(self):
        return "%s %s" % (self.first_name, self.last_name)

    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name']}
    addresses = one2many("addresses", "bungeni.models.domain.UserAddressContainer", "user_id")
    delegations = one2many("delegations", "bungeni.models.domain.UserDelegationContainer", "user_id")
    _password = property(getPassword, setPassword)

    bills = one2many("bills", "bungeni.models.domain.BillContainer", "owner_id")
    questions = one2many("questions",
        "bungeni.models.domain.QuestionContainer", "owner_id")
    motions = one2many("motions",
        "bungeni.models.domain.MotionContainer", "owner_id")
    agendaitems = one2many("agendaitems",
        "bungeni.models.domain.AgendaItemContainer", "owner_id")
    tableddocuments = one2many("tableddocuments",
        "bungeni.models.domain.TabledDocumentContainer", "owner_id")

class UserDelegation(Entity):
    """ Delgate rights to act on behalf of a user 
    to another user """


#class HansardReporter(User):
#    """ a reporter who reports on parliamentary procedings
#    """

    # rotas

    # takes

######

class Group(Entity):
    """ an abstract collection of users
    """
    interface.implements(interfaces.IBungeniGroup, interfaces.ITranslatable)

    #users = one2many("users", "bungeni.models.domain.GroupMembershipContainer", "group_id")
    #sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")

    def active_membership(self, user_id):
        session = Session()
        query = session.query(GroupMembership).filter(
            sql.and_(GroupMembership.group_id == self.group_id,
                    GroupMembership.user_id == user_id,
                    GroupMembership.active_p == True
                )
            )
        if query.count() == 0:
            return False
        else:
            return True



class GroupMembership(Entity):
    """ a user's membership in a group- abstract
    basis for ministers, committeemembers, etc
    """
    interface.implements(interfaces.IBungeniGroupMembership, interfaces.ITranslatable)
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name']}

    @property
    def image(self):
        return self.user.image



class OfficesHeld(Entity):
    """ Offices held by this group member """

class ListCommitteeStaff(object):
    pass

class CommitteeStaff(GroupMembership):
    """
    Comittee Staff
    """
    titles = one2many("titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListCommitteeStaff

class GroupSitting(Entity):
    """Scheduled meeting for a group (parliament, committee, etc)"""
    interface.implements(interfaces.ITranslatable)

    attendance = one2many(
        "attendance", "bungeni.models.domain.GroupSittingAttendanceContainer", "sitting_id")

    items = one2many(
        "items", "bungeni.models.domain.ItemScheduleContainer", "sitting_id")

    sreports = one2many(
        "sreports", "bungeni.models.domain.Report4SittingContainer", "sitting_id")

    @property
    def short_name(self):
        return self.start_date.strftime('%d %b %y %H:%M')


class SittingType(object):
    """ Type of sitting: morning/afternoon/... """
    interface.implements(interfaces.ITranslatable)

class ListGroupSittingAttendance(object):
    pass

class GroupSittingAttendance(object):
    """ a record of attendance at a meeting 
    """
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'member_id': ['last_name', 'first_name', ]}
    listings_class = ListGroupSittingAttendance

class AttendanceType(object):
    """
    lookup for attendance type
    """
    interface.implements(interfaces.ITranslatable)

class ListGroupItemAssignment(object):
    pass


class GroupItemAssignment(object):
    """ the assignment of a parliamentary content object to a group
    """
    interface.implements(interfaces.ITranslatable)
    listings_class = ListGroupItemAssignment


class GroupGroupItemAssignment(GroupItemAssignment):
    """ assign a group to an item """


class ItemGroupItemAssignment(GroupItemAssignment):
    """ assign an item to a group """


#############

class ListParliament(object):
    pass

class Parliament(Group):
    """ a parliament
    """
    sort_on = ['start_date']
    sessions = one2many("sessions", "bungeni.models.domain.ParliamentSessionContainer", "parliament_id")
    committees = one2many("committees", "bungeni.models.domain.CommitteeContainer", "parent_group_id")
    governments = one2many("governments", "bungeni.models.domain.GovernmentContainer", "parent_group_id")
    parliamentmembers = one2many("parliamentmembers",
                                 "bungeni.models.domain.MemberOfParliamentContainer", "group_id")
    politicalgroups = one2many("politicalgroups", "bungeni.models.domain.PoliticalGroupContainer", "parent_group_id")
    bills = one2many("bills", "bungeni.models.domain.BillContainer", "parliament_id")
    questions = one2many("questions", "bungeni.models.domain.QuestionContainer", "parliament_id")
    motions = one2many("motions", "bungeni.models.domain.MotionContainer", "parliament_id")
    sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")
    offices = one2many("offices", "bungeni.models.domain.OfficeContainer", "parent_group_id")
    agendaitems = one2many("agendaitems", "bungeni.models.domain.AgendaItemContainer", "group_id")
    tableddocuments = one2many("tableddocuments", "bungeni.models.domain.TabledDocumentContainer", "parliament_id")
    preports = one2many("preports", "bungeni.models.domain.ReportContainer", "group_id")
    listings_class = ListParliament


class ListMemberOfParliament(object):
    """
    Listing for the parliament membership
    """
class MemberOfParliament(GroupMembership):
    """
    defined by groupmembership and additional data
    """
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {"user_id": ["last_name", "first_name"],
        "constituency_id":["name"], "province_id":["name"], 
        "region_id":["name"], "party_id":["name"]}
    titles = one2many("titles",
        "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListMemberOfParliament

class PoliticalEntity(Group):
    """ Base class for political parties and political groups """
    interface.implements(interfaces.ITranslatable)

class PoliticalParty(PoliticalEntity):
    """ a political party (ouside the parliament)
    """
    partymembers = one2many("partymembers",
        "bungeni.models.domain.PartyMemberContainer", "group_id")

class PoliticalGroup(PoliticalEntity):
    """ a political group in a parliament
    """
    partymembers = one2many("partymembers", "bungeni.models.domain.PartyMemberContainer", "group_id")

class ListPartyMember(object):
    pass

class PartyMember(GroupMembership):
    """ 
    Member of a political party or group, defined by its group membership 
    """
    titles = one2many("titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListPartyMember


class ListGovernment(object):
    pass

class Government(Group):
    """ a government
    """
    sort_on = ['start_date']
    ministries = one2many("ministries", "bungeni.models.domain.MinistryContainer", "parent_group_id")
    listings_class = ListGovernment

class Ministry(Group):
    """ a government ministry
    """
    ministers = one2many("ministers", "bungeni.models.domain.MinisterContainer", "group_id")
    questions = one2many("questions", "bungeni.models.domain.QuestionContainer", "ministry_id")
    bills = one2many("bills", "bungeni.models.domain.BillContainer", "ministry_id")

class ListMinister(object):
    pass

class Minister(GroupMembership):
    """ A Minister
    defined by its user_group_membership in a ministry (group)
    """
    titles = one2many("titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListMinister


class ListCommittee(object):
    pass

class Committee(Group):
    """ a parliamentary committee of MPs
    """
    committeemembers = one2many("committeemembers", "bungeni.models.domain.CommitteeMemberContainer", "group_id")
    committeestaff = one2many("committeestaff", "bungeni.models.domain.CommitteeStaffContainer", "group_id")
    agendaitems = one2many("agendaitems", "bungeni.models.domain.AgendaItemContainer", "group_id")
    sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")
    sort_replace = {'committee_type_id': ['committee_type', ]}
    assigneditems = one2many("assigneditems", "bungeni.models.domain.ItemGroupItemAssignmentContainer", "group_id")
    listings_class = ListCommittee

class ListCommitteeMember(object):
    pass

class CommitteeMember(GroupMembership):
    """ A Member of a committee
    defined by its membership to a committee (group)"""

    titles = one2many("titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListCommitteeMember

class CommitteeType(object):
    """ Type of Committee """
    interface.implements(interfaces.ITranslatable)

class Office(Group):
    """ parliamentary Office like speakers office,
    clerks office etc. internal only"""
    officemembers = one2many("officemembers", "bungeni.models.domain.OfficeMemberContainer", "group_id")

class ListOfficeMember(object):
    pass

class OfficeMember(GroupMembership):
    """ clerks, .... """
    titles = one2many("titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id")
    listings_class = ListOfficeMember


#class Debate(Entity):
#    """
#    Debates
#    """

class AddressType(object):
    """
    Address Types
    """
    interface.implements(interfaces.ITranslatable)

class UserAddress(Entity):
    """
    addresses of a user
    """


#############

class ItemLog(object):
    """ an audit log of events in the lifecycle of a parliamentary content
    """
    @classmethod
    def makeLogFactory(klass, name):
        factory = type(name, (klass,), {})
        interface.classImplements(factory, interfaces.IChange)
        return factory

class ItemVersions(Entity):
    """a collection of the versions of a parliamentary content object
    """
    @classmethod
    def makeVersionFactory(klass, name):
        factory = type(name, (klass,), {})
        interface.classImplements(factory, interfaces.IVersion)
        return factory

    #files = one2many("files", "bungeni.models.domain.AttachedFileContainer", "file_version_id")



class ItemVotes(object):
    """
    """

class ParliamentaryItem(Entity):
    """
    """
    interface.implements(interfaces.IBungeniContent, interfaces.ITranslatable)
    #     interfaces.IHeadFileAttachments)
    sort_replace = {'owner_id': ['last_name', 'first_name']}
    files = one2many("files", "bungeni.models.domain.AttachedFileContainer", "item_id")
    # votes

    # schedule

    # object log

    # versions



class AttachedFile(Entity):
    "Files attached to a parliamentary item"
    versions = one2many(
        "versions",
        "bungeni.models.domain.AttachedFileVersionContainer",
        "content_id")

AttachedFileChange = ItemLog.makeLogFactory("AttachedFileChange")
AttachedFileVersion = ItemVersions.makeVersionFactory("AttachedFileVersion")


class ListHeading(object):
    pass

class Heading(ParliamentaryItem):
    """ A heading in a report """
    listings_class = ListHeading
    interface.implements(interfaces.ITranslatable)

class ListAgendaItem(object):
    pass

class AgendaItem(ParliamentaryItem):
    """
    Generic Agenda Item that can be scheduled on a sitting
    """

    versions = one2many(
        "versions",
        "bungeni.models.domain.AgendaItemVersionContainer",
        "content_id")
    listings_class = ListAgendaItem

AgendaItemChange = ItemLog.makeLogFactory("AgendaItemChange")
AgendaItemVersion = ItemVersions.makeVersionFactory("AgendaItemVersion")

class ListQuestion(object):
    pass

class Question(ParliamentaryItem):
    #supplementaryquestions = one2many("supplementaryquestions", 
    #"bungeni.models.domain.QuestionContainer", "supplement_parent_id")
    event = one2many("event", "bungeni.models.domain.EventItemContainer", "item_id")
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")
    versions = one2many(
        "versions",
        "bungeni.models.domain.QuestionVersionContainer",
        "content_id")
    sort_on = ['question_number', 'submission_date']
    sort_dir = 'desc'
    listings_class = ListQuestion

    def getParentQuestion(self):
        if self.supplement_parent_id:
            session = Session()
            parent = session.query(Question).get(self.supplement_parent_id)
            return parent.short_name




QuestionChange = ItemLog.makeLogFactory("QuestionChange")
QuestionVersion = ItemVersions.makeVersionFactory("QuestionVersion")

class ListMotion(object):
    pass


class Motion(ParliamentaryItem):
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")
    event = one2many("event", "bungeni.models.domain.EventItemContainer", "item_id")
    versions = one2many(
        "versions",
        "bungeni.models.domain.MotionVersionContainer",
        "content_id")

    sort_on = ['motion_number', 'submission_date']
    sort_dir = 'desc'
    listings_class = ListMotion

MotionChange = ItemLog.makeLogFactory("MotionChange")
MotionVersion = ItemVersions.makeVersionFactory("MotionVersion")


class BillType(object):
    """
    type of bill: public/ private, ....
    """

class ListBill(object):
    pass

class Bill(ParliamentaryItem):
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")
    event = one2many("event", "bungeni.models.domain.EventItemContainer", "item_id")
    assignedgroups = one2many("assignedgroups", "bungeni.models.domain.GroupGroupItemAssignmentContainer", "item_id")

    versions = one2many(
        "versions",
        "bungeni.models.domain.BillVersionContainer",
        "content_id")
    sort_on = ['submission_date']
    sort_dir = 'desc'
    listings_class = ListBill

BillChange = ItemLog.makeLogFactory("BillChange")
BillVersion = ItemVersions.makeVersionFactory("BillVersion")

class ListConsignatory(object):
    pass

class Consignatory(Entity):
    """
    Consignatories for a Bill or Motion
    """
    listings_class = ListConsignatory


#############

class ParliamentSession(Entity):
    """
    """
    sort_on = ['start_date', ]
    sort_dir = 'desc'
    interface.implements(interfaces.ITranslatable)

class Rota(object):
    """
    """

class Take(object):
    """
    """

class TakeMedia(object):
    """
    """

class Transcript(object):
    """
    """


class ObjectSubscriptions(object):
    """
    """

# ###############

class ListConstituency(object):
    pass

class Constituency(Entity):
    """ a locality region, which elects an MP 
    """
    cdetail = one2many("cdetail",
        "bungeni.models.domain.ConstituencyDetailContainer", "constituency_id")
    #sort_replace = {'province_id': ['province'], 'region_id': ['region']}
    parliamentmembers = one2many("parliamentmembers",
        "bungeni.models.domain.MemberOfParliamentContainer", "constituency_id")
    listings_class = ListConstituency
    interface.implements(interfaces.ITranslatable)

#ConstituencyChange = ItemLog.makeLogFactory("ConstituencyChange")
#ConstituencyVersion = ItemVersions.makeVersionFactory("ConstituencyVersion")

class Region(Entity):
    """
    Region of the constituency
    """
    #constituencies = one2many("constituencies",
    #    "bungeni.models.domain.ConstituencyContainer", "region_id")
    interface.implements(interfaces.ITranslatable)

class Province(Entity):
    """
    Province of the Constituency
    """
    #constituencies = one2many("constituencies",
    #    "bungeni.models.domain.ConstituencyContainer", "province_id")
    interface.implements(interfaces.ITranslatable)

class Country(object):
    """
    Country of Birth
    """
    pass

class ConstituencyDetail(object):
    """
    Details of the Constituency like population and voters at a given time
    """
    pass


# ##########


class MemberTitle(object):
    """ Titles for members in groups"""
    interface.implements(interfaces.ITranslatable)


class MemberRoleTitle(Entity):
    """
    The role title a member has in a specific context
    and one official addresse for a official role
    """
    interface.implements(interfaces.ITranslatable)


class MinistryInParliament(object):
    """
    auxilliary class to get the parliament and government for a ministry
    """

class ItemSchedule(Entity):
    """
    for which sitting was a parliamentary item scheduled
    """

    discussions = one2many(
        "discussions",
        "bungeni.models.domain.ScheduledItemDiscussionContainer",
        "schedule_id")

    @property
    def getItem(self):
        session = Session()
        s_item = self.item
        s_item.__parent__ = self
        return s_item

    @property
    def getDiscussion(self):
        session = Session()
        s_discussion = self.discussion
        s_discussion.__parent__ = self
        return s_discussion


class ScheduledItemDiscussion(Entity):
    """A discussion on a scheduled item."""
    interface.implements(interfaces.ITranslatable)

class ListTabledDocument(object):
    pass

class TabledDocument(ParliamentaryItem):
    """
    Tabled documents:
    a tabled document captures metadata about the document (owner, date, title, description) 
    and can have multiple physical documents attached.

        The tabled documents form should have the following :

    -Document title
    -Document link
    -Upload field (s)
    -Document source  / author agency (who is providing the document)
    (=> new table agencies)

    -Document submitter (who is submitting the document)
    (a person -> normally mp can be other user)

    It must be possible to schedule a tabled document for a sitting.
    """
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")
    event = one2many("event", "bungeni.models.domain.EventItemContainer", "item_id")
    versions = one2many(
        "versions",
        "bungeni.models.domain.TabledDocumentVersionContainer",
        "content_id")
    listings_class = ListTabledDocument


TabledDocumentChange = ItemLog.makeLogFactory("TabledDocumentChange")
TabledDocumentVersion = ItemVersions.makeVersionFactory("TabledDocumentVersion")



class DocumentSource(object):
    """
    Document source for a tabled document
    """

class ListEventItem(object):
    pass

class EventItem(ParliamentaryItem):
    """
    Bill events with dates and possiblity to upload files.

    bill events have a title, description and may be related to a sitting (house, committee or other group sittings)
    via the sitting they acquire a date
    and an additional date for items that are not related to a sitting.

    Bill events:

       1. workflow related. e.g. submission, first reading etc. 
       (here we can use the same mechanism as in questions ... 
       a comment can be written when clicking (schedule for first reading) 
       then will appear in the calendar ... and cone schedule it will have a date
       2. not workflow related events ... we need for the following fieds:
              * date
              * body
              * attachments

    All these "events" they may be listed together, in that case the "workflow" once should be ... e.g. in bold.
    """
    listings_class = ListEventItem

class HoliDay(object):
    """
    is this day a holiday?
    if a date in in the table it is otherwise not
    """


class Resource (object):
    """
    A Resource that can be assigned to a sitting
    """

class ResourceBooking (object):
    """
    assign a resource to a sitting
    """
class ResourceType(object):
    """ A Type of resource"""

class Venue(object):
    """ A venue for a sitting """

class Report(ParliamentaryItem):
    """ agendas and minutes """
    interface.implements(interfaces.ITranslatable)

class SittingReport(Report):
    """ which reports are created for this sitting"""

class Report4Sitting(Report):
    """ display reports for a sitting"""

class ObjectTranslation(object):
    """ get the translations for an Object"""

