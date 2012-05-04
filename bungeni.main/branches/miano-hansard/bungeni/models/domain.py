# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni object domain

Created by Kapil Thangavelu on 2007-11-22.

$Id$
"""
log = __import__("logging").getLogger("bungeni.models.domain")

import md5, random, string
import datetime

from zope import interface, location
import ore.xapian.interfaces
from bungeni.alchemist import Session
from bungeni.alchemist import model
from bungeni.alchemist.traversal import one2many, one2manyindirect
import sqlalchemy.sql.expression as sql
from sqlalchemy.orm import class_mapper, object_mapper

import interfaces

from bungeni.utils.capi import capi


def object_hierarchy_type(object):
    if isinstance(object, User):
        return "user"
    if isinstance(object, Group):
        return "group"
    if isinstance(object, Doc):
        return "doc"
    return ""


CHANGE_ACTIONS = ("add", "modify", "workflow", "remove", "version", "reversion")

def assert_valid_change_action(action):
    assert action in CHANGE_ACTIONS, \
        "Invalid audit action: %s. Must be one of: %s" % (
            action, CHANGE_ACTIONS)

def get_changes(auditable, *actions):
    """Get changelog for auditable context, filtered for actions.
    """
    for action in actions:
        assert_valid_change_action(action)
    # lazy loading - merge to avoid sqlalchemy.orm.exc.DetachedInstanceError
    auditable = Session().merge(auditable)
    return [ c for c in auditable.changes if c.action in actions ]

def get_mapped_table(kls):
    return class_mapper(kls).mapped_table

def get_audit_table_name(kls):
    return "%s_audit" % (get_mapped_table(kls).name)

def get_mapped_object_id(ob):
    return object_mapper(ob).primary_key_from_instance(ob)[0]

#

class HeadParentedMixin(object):
    """For sub-objects of a "head" object.
    
    Changes the behaviour of __parent__ to by default return the head object 
    UNLESS a non-None __parent__ is hard-set explicitly set on the sub-instance
    (e.g. as within an alchemist container listing, alchemist sets the 
    __parent__ to the container).
    
    This default behaviour is needed as the roles a user has via a 
    sub-object may not include all the same roles the user has on its 
    head object, that may result in an incorrect permission decision,
    in particular as permission checking on sub-objects is often bound
    to permissions on the head object.
    """
    # remember if __parent__ has been explicitly set
    _explicit_parent = None
    # implement as a "clean" property, using the namespace containment of a 
    # "temporary" function, that returns a dict to be later used as keyword
    # args to define a same-named property.
    def __parent__():
        doc = "Returns the Zope 3 canonical location of the instance " \
            "i.e. the __parent__ object, usually needed to lookup security " \
            "settings on the instance."
        def fget(self):
            if self._explicit_parent is None:
                return self.head
            return self._explicit_parent
        def fset(self, parent):
            self._explicit_parent = parent
        def fdel(self):
            self._explicit_parent = None
        return locals()
    __parent__ = property(**__parent__())


class Entity(object):
    interface.implements(location.ILocation)
    __name__ = None
    __parent__ = None
    
    # !+ base archetype
    __dynamic_features__ = False
    
    extended_properties = [] # [(name, type)]
    
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
                log.error(
                    "Invalid attribute on %s %s" % (
                        self.__class__.__name__, k))
    
    # sort_on: the list of column names the query is sorted on by default
    sort_on = None
    
    # sort_dir = desc | asc
    #sort_dir = "desc"
    
    # sort_replace: a dictionary that maps one column to another
    # so when the key is requested in a sort the value gets sorted
    # eg: {"user_id":"sort_name"} when the sort on user_id is requested the 
    # query gets sorted by sort_name
    #sort_replace = None

#

# !+PARAMETRIZABLE_DOCTYPES(mr, jun-2011) the quality of a domain type to
# be auditable or versionable is externalized as a localization parameter, and
# its implementation must thus be completely isolated, depending only on that
# one declaration.

# Handling of dynamic features (as per a deployment's configuration)
# Note: in a simplified one-generic-document-type world, these can be 
# simplified even further. 

def CREATE_AUDIT_CLASS_FOR(cls):
    """Is the audit_cls for this kls created dynamically?"""
    return cls in CREATE_AUDIT_CLASS_FOR.classes
CREATE_AUDIT_CLASS_FOR.classes = []


def configurable_domain(kls, workflow):
    assert kls.__dynamic_features__, \
        "Class [%s] does not allow dynamic features" % (kls)
    # note: versionable implies auditable
    for feature in workflow.features:
        if feature.enabled:
            kls = configurable_domain.feature_decorators[feature.name](kls)
    return kls
configurable_domain.feature_decorators = {}

# convenience, per decorator name, remember decorated types
CUSTOM_DECORATED = {
    # decorator_name: set([kls])
    "auditable": set(), # [kls]
    "versionable": set(), # [kls]
    "enable_attachment": set(), # [kls]
    "enable_schedule": set(), # [kls]
}

def auditable(kls):
    """Decorator for auditable domain types, to collect in one place all
    that is needed for a domain type to be auditale.
    
    Executed on adapters.load_workflow()
    """
    CUSTOM_DECORATED["auditable"].add(kls)
    interface.classImplements(kls, interfaces.IAuditable)
    # If a domain class is explicitly defined, then it is assumed that all 
    # necessary setup is also taken care of. Typically, only the sub-classes
    # of an archetype (mapped to a same table) need dynamic creation/setup.
    def audit_cls_exists_for(auditable_cls):
        audit_cls_name = "%sAudit" % (auditable_cls.__name__)
        return bool(globals().get(audit_cls_name))
    if not audit_cls_exists_for(kls):
        CREATE_AUDIT_CLASS_FOR.classes.append(kls)
    if CREATE_AUDIT_CLASS_FOR(kls):
        # define {kls}Audit class
        def base_audit_class(kls):
            """Identify what should be the BASE audit class for a 
            {kls}Audit class to inherit from, and return it.
            """
            # !+ may have a deeper inheritance
            # !+ other achetypes
            if kls is not Doc and issubclass(kls, Doc):
                return DocAudit
            return Audit
        audit_kls = base_audit_class(kls).auditFactory(kls)
        globals()[audit_kls.__name__] = audit_kls
    return kls
configurable_domain.feature_decorators["audit"] = auditable

def versionable(kls):
    """Decorator for versionable domain types, to collect in one place all
    that is needed for a domain type to be versionable.
    
    Executed on adapters.load_workflow()
    
    Note: @versionable implies @auditable
    """
    CUSTOM_DECORATED["versionable"].add(kls)
    assert interfaces.IAuditable.implementedBy(kls)
    # assign interface (versions property added downstream)
    interface.classImplements(kls, interfaces.IVersionable)
    return kls
configurable_domain.feature_decorators["version"] = versionable

def enable_attachment(kls):
    """Decorator for attachment-feature of domain types.
    Executed on adapters.load_workflow()
    
    !+ currently assumes that the object is versionable.
    """
    # !+ domain.Attachment is versionable, but does not support attachments
    CUSTOM_DECORATED["enable_attachment"].add(kls)
    interface.classImplements(kls, interfaces.IAttachmentable)
    return kls
configurable_domain.feature_decorators["attachment"] = enable_attachment

def enable_schedule(kls):
    """Decorator for schedulable types
    """
    CUSTOM_DECORATED["enable_schedule"].add(kls)
    interface.classImplements(kls, interfaces.ISchedulable)
    return kls
configurable_domain.feature_decorators["schedule"] = enable_schedule

# !+/PARAMETRIZABLE_DOCTYPES

class User(Entity):
    """Domain Object For A User. General representation of a person.
    """
    __dynamic_features__ = True
    
    interface.implements(interfaces.IBungeniUser, interfaces.ITranslatable)
    
    def __init__(self, login=None, **kw):
        if login:
            self.login = login
        super(User, self).__init__(**kw)
        self.salt = self._makeSalt()

    def _makeSalt(self):
        return "".join(random.sample(string.letters[:52], 12))

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

    sort_on = ["last_name", "first_name", "middle_name"]
    sort_replace = {"user_id": ["last_name", "first_name"]}
    sort_dir = "asc"
    addresses = one2many("addresses",
        "bungeni.models.domain.UserAddressContainer", "user_id")
    delegations = one2many("delegations",
        "bungeni.models.domain.UserDelegationContainer", "user_id")
    _password = property(getPassword, setPassword)

    bills = one2many("bills",
        "bungeni.models.domain.BillContainer", "owner_id")
    questions = one2many("questions",
        "bungeni.models.domain.QuestionContainer", "owner_id")
    motions = one2many("motions",
        "bungeni.models.domain.MotionContainer", "owner_id")
    agendaitems = one2many("agendaitems",
        "bungeni.models.domain.AgendaItemContainer", "owner_id")
    tableddocuments = one2many("tableddocuments",
        "bungeni.models.domain.TabledDocumentContainer", "owner_id")

class AdminUser(Entity):
    """An admin user"""

class UserDelegation(Entity):
    """ Delgate rights to act on behalf of a user 
    to another user """
    
class CurrentlyEditingDocument(object):
    """The document (parliamentary item) 
    that the user is currently being editing"""
    
class PasswordRestoreLink(object):
    """Object containing hash and expiration date for
    password restoration form"""
    
    def expired(self):
        return self.expiration_date < datetime.datetime.now() 

#class HansardReporter(User):
#    """ a reporter who reports on parliamentary procedings
#    """
#    rotas
#    takes


######

class Group(Entity):
    """ an abstract collection of users
    """
    __dynamic_features__ = True # !+ False
    interface.implements(interfaces.IBungeniGroup, interfaces.ITranslatable)
    sort_on = ["short_name", "full_name"]
    sort_dir = "asc"
    sort_replace = {"group_id": ["short_name", ]}
    #users = one2many("users", 
    #   "bungeni.models.domain.GroupMembershipContainer", "group_id")
    #sittings = one2many("sittings", 
    #   "bungeni.models.domain.SittingContainer", "group_id")
    
    addresses = one2many("addresses",
        "bungeni.models.domain.GroupAddressContainer", "group_id"
    )
    headings = one2many("headings", "bungeni.models.domain.HeadingContainer",
        "group_id"
    )
    editorial_notes = one2many("editorialnotes", 
        "bungeni.models.domain.EditorialNoteContainer",
        "group_id"
    )
    def active_membership(self, user_id):
        session = Session()
        query = session.query(GroupMembership).filter(
            sql.and_(
                GroupMembership.group_id == self.group_id,
                GroupMembership.user_id == user_id,
                GroupMembership.active_p == True
            )
        )
        if query.count() == 0:
            return False
        else:
            return True


class GroupMembership(HeadParentedMixin, Entity):
    """A user's membership in a group-abstract basis for 
    ministers, committeemembers, etc.
    """
    __dynamic_features__ = False
    interface.implements(
        interfaces.IBungeniGroupMembership, interfaces.ITranslatable)
    sort_on = ["last_name", "first_name", "middle_name"]
    sort_replace = {"user_id": ["last_name", "first_name"]}
    sort_dir = "asc"
    
    @property
    def image(self):
        return self.user.image


class OfficesHeld(Entity):
    """Offices held by this group member.
    """

class CommitteeStaff(GroupMembership):
    """Committee Staff.
    """
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")


# auditable (by default), but not a Doc
class Sitting(Entity):
    """Scheduled meeting for a group (parliament, committee, etc).
    """
    interface.implements(
        interfaces.ITranslatable,
        interfaces.IDocument, # !+IDoc?
    )

    __dynamic_features__ = True # !+ False

    attendance = one2many("attendance",
        "bungeni.models.domain.SittingAttendanceContainer", "sitting_id")
    items = one2many("items",
        "bungeni.models.domain.ItemScheduleContainer", "sitting_id")
    sreports = one2many("sreports",
        "bungeni.models.domain.Report4SittingContainer", "sitting_id")

class SittingAttendance(object):
    """A record of attendance at a meeting .
    """
    sort_on = ["last_name", "first_name", "middle_name"]
    sort_replace = {"member_id": ["last_name", "first_name", ]}

''' !+TYPES_CUSTOM
class AttendanceType(Entity):
    """Lookup for attendance type.
    """
    interface.implements(interfaces.ITranslatable,
        interfaces.IAttendanceType
    )
'''

#############

class Parliament(Group):
    """A parliament.
    """
    sort_on = ["start_date"]
    sessions = one2many("sessions",
        "bungeni.models.domain.ParliamentSessionContainer", "parliament_id")
    committees = one2many("committees",
        "bungeni.models.domain.CommitteeContainer", "parent_group_id")
    governments = one2many("governments",
        "bungeni.models.domain.GovernmentContainer", "parent_group_id")
    parliamentmembers = one2many("parliamentmembers",
        "bungeni.models.domain.MemberOfParliamentContainer", "group_id")
    politicalgroups = one2many("politicalgroups",
        "bungeni.models.domain.PoliticalGroupContainer", "parent_group_id")
    bills = one2many("bills",
        "bungeni.models.domain.BillContainer", "parliament_id")
    questions = one2many("questions",
        "bungeni.models.domain.QuestionContainer", "parliament_id")
    motions = one2many("motions",
        "bungeni.models.domain.MotionContainer", "parliament_id")
    sittings = one2many("sittings",
        "bungeni.models.domain.SittingContainer", "group_id")
    agendaitems = one2many("agendaitems",
        "bungeni.models.domain.AgendaItemContainer", "group_id")
    tableddocuments = one2many("tableddocuments",
        "bungeni.models.domain.TabledDocumentContainer", "parliament_id")
    preports = one2many("preports",
        "bungeni.models.domain.ReportContainer", "group_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")

class MemberOfParliament(GroupMembership):
    """Defined by groupmembership and additional data.
    """
    sort_on = ["last_name", "first_name", "middle_name"]
    sort_replace = {"user_id": ["last_name", "first_name"],
        "constituency_id":["name"], "province_id":["name"],
        "region_id":["name"], "party_id":["name"]}
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")
    addresses = one2manyindirect("addresses", 
        "bungeni.models.domain.UserAddressContainer", "user_id")

class PoliticalEntity(Group):
    """Base class for political parties and political groups.
    """
    interface.implements(interfaces.ITranslatable)
    
class PoliticalParty(PoliticalEntity):
    """A political party (ouside the parliament).
    """
    partymembers = one2many("partymembers",
        "bungeni.models.domain.PartyMemberContainer", "group_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")
class PoliticalGroup(PoliticalEntity):
    """A political group in a parliament.
    """
    partymembers = one2many("partymembers",
        "bungeni.models.domain.PartyMemberContainer", "group_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")
class PartyMember(GroupMembership):
    """Member of a political party or group, defined by its group membership.
    """
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")

class Government(Group):
    """A government.
    """
    sort_on = ["start_date"]
    ministries = one2many("ministries",
        "bungeni.models.domain.MinistryContainer", "parent_group_id")

class Ministry(Group):
    """A government ministry.
    """
    ministers = one2many("ministers",
        "bungeni.models.domain.MinisterContainer", "group_id")
    questions = one2many("questions",
        "bungeni.models.domain.QuestionContainer", "ministry_id")
    bills = one2many("bills",
        "bungeni.models.domain.BillContainer", "ministry_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")
class Minister(GroupMembership):
    """A Minister defined by its user_group_membership in a ministry (group).
    """
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")


class Committee(Group):
    """A parliamentary committee of MPs.
    """
    # !+ManagedContainer(mr, oct-2010) why do all these Managed container 
    # attributes return a list of processed-id-derived strings instead of the 
    # list of actual objects in question? 
    # e.g. committee.committeemembers returns: ['obj-41', 'obj-42']
    #
    committeemembers = one2many("committeemembers",
        "bungeni.models.domain.CommitteeMemberContainer", "group_id")
    committeestaff = one2many("committeestaff",
        "bungeni.models.domain.CommitteeStaffContainer", "group_id")
    agendaitems = one2many("agendaitems",
        "bungeni.models.domain.AgendaItemContainer", "group_id")
    sittings = one2many("sittings",
        "bungeni.models.domain.SittingContainer", "group_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")

class CommitteeMember(GroupMembership):
    """A Member of a committee defined by its membership to a committee (group).
    """
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")

''' !+TYPES_CUSTOM
class CommitteeType(Entity):
    """Type of Committee.
    """
    interface.implements(interfaces.ITranslatable,
        interfaces.ICommitteeType
    )
'''

class Office(Group):
    """Parliamentary Office like speakers office, clerks office etc. 
    Internal only.
    """
    officemembers = one2many("officemembers",
        "bungeni.models.domain.OfficeMemberContainer", "group_id")
    title_types = one2many("title_types",
        "bungeni.models.domain.TitleTypeContainer", "group_id")

class OfficeMember(GroupMembership):
    """Clerks, .... 
    """
    titles = one2many("titles",
        "bungeni.models.domain.MemberTitleContainer", "membership_id")


#class Debate(Entity):
#    """
#    Debates
#    """

class Address(HeadParentedMixin, Entity):
    """Address base class
    """
    __dynamic_features__ = False
    # !+ note corresponding tbls exist only for subclasses
class UserAddress(Address):
    """User address (personal)
    """
class GroupAddress(Address):
    """Group address (official)
    """


# extended attributes - vertical properties

# !+could use __metaclass__ but that causes internal breaks elsewhere...
# !+could be a class decorator 
def instrument_extended_properties(cls, object_type, from_class=None):
    # !+class not yet mapped
    #object_type = class_mapper(cls).local_table.name 
    if from_class is None:
        from_class = cls
    # ensure cls.__dict__.extended_properties
    cls.extended_properties = cls.extended_properties[:]
    for vp_name, vp_type in from_class.extended_properties:
        if (vp_name, vp_type) not in cls.extended_properties:
            cls.extended_properties.append((vp_name, vp_type))
        setattr(cls, vp_name, vertical_property(object_type, vp_name, vp_type))

def vertical_property(object_type, vp_name, vp_type, *args, **kw):
    """Get the external (non-SQLAlchemy) extended Vertical Property
    (on self.__class__) as a regular python property.
    
    !+ Any additional args/kw are exclusively for instantiation of vp_type.
    """
    _vp_name = "_vp_%s" % (vp_name) # name for SA mapper property for this
    doc = "VerticalProperty %s of type %s" % (vp_name, vp_type)
    def fget(self):
        vp = getattr(self, _vp_name, None)
        if vp is not None:
            return vp.value
    def fset(self, value):
        vp = getattr(self, _vp_name, None)
        if vp is not None:
            vp.value = value
        else: 
            vp = vp_type(self, object_type, vp_name, value, *args, **kw)
            setattr(self, _vp_name, vp)
    def fdel(self):
        setattr(self, _vp_name, None)
    return property(fget=fget, fset=fset, fdel=fdel, doc=doc)

class VerticalProperty(Entity):
    """Base Vertical Property.
    """
    def __init__(self, object_, object_type, name, value):
        # !+backref sqlalchemy populates a self.object backref, but on flushing
        self._object = object_
        # sqlalchemy instruments a property per column, of same name
        self.object_id = get_mapped_object_id(object_)
        self.object_type = object_type # the db table's name
        self.name = name # the domain class's property name
        self.value = value
    
    def __repr__(self):
        return "<%s %s=%r on (%r, %s) at %s>" % (self.__class__.__name__, 
                self.name, self.value, 
                self.object_type, self.object_id, hex(id(self._object)))

class vp(object):
    """A convenient vp namespace.
    """
    class Text(VerticalProperty):
        """VerticalProperty of type text.
        """
    class TranslatedText(VerticalProperty):
        """VerticalProperty of type translated text.
        """
        def __init__(self, object_, object_type, name, value, language=None):
            VerticalProperty.__init__(self, object_, object_type, name, value)
            # !+LANGUAGE(mr, mar-2012) using "en" as default... as
            # get_default_language() is in core, that *depends* on models!
            self.language = language or "en" # or get_default_language()

#

class Doc(Entity):
    """Base class for a workflowed parliamentary document.
    """
    __dynamic_features__ = True
    
    interface.implements(
        interfaces.IDocument, # !+IDoc?
        interfaces.IBungeniParliamentaryContent, #!+should be applied as needed?
        interfaces.ITranslatable
    )
    
    sort_on = ["doc.status_date", "doc.type_number"]
    sort_dir = "desc"
    
    sort_replace = {"owner_id": ["last_name", "first_name"]}
    
    # !+AlchemistManagedContainer these attribute names are part of public URLs!
    # !+item_id->head_id
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
    
    def _get_workflow_date(self, *states):
        """ (states:seq(str) -> date
        Get the date of the most RECENT workflow transition to any one of 
        the workflow states specified as input parameters. 
        
        Returns None if no such workflow states has been transited to as yet.
        """
        assert states, "Must specify at least one workflow state."
        # order of self.changes is reverse chronological (newest first)
        for c in get_changes(self, "workflow"):
            if c.audit.status in states:
                return c.date_active
    
    @property
    def submission_date(self):
        # As base meaning of "submission_date" we take the most recent date
        # of workflow transition to "submit" to clerk. Subclasses may need
        # to overload as appropriate for their respective workflows.
        return self._get_workflow_date("submitted")
    
    extended_properties = [
    ]
instrument_extended_properties(Doc, "doc")


class AdmissibleMixin(object):
    """Assumes self._get_workflow_date().
    """
    @property
    def admissible_date(self):
        return self._get_workflow_date("admissible")


class Change(HeadParentedMixin, Entity):
    """Information about a change.
    """
    __dynamic_features__ = False
    interface.implements(
        interfaces.IChange
    )
    
    @property
    def head(self):
        return self.audit.audit_head # orm property
    
    # !+Change.status(mr, apr-2012) needed? keep?
    @property
    def status(self):
        return self.audit.status # assumption: audit.audit_head is workflowed
    
    def get_seq_previous(self):
        """Get the previous change in this seq of actions. 
        Returns None if no previous.
        """
        changes = get_changes(self.head, self.action)
        for c in changes[1 + changes.index(self):]:
            return c
    
    # change "note" -- as external extended attribute (vertical property) as:
    # a) presumably it may have to be translatable, and the initial language 
    #    may not be the same as that of the head object being audited.
    # b) it will be set very seldom.
    extended_properties = [
        ("note", vp.TranslatedText)
    ]
instrument_extended_properties(Change, "change")

class ChangeTree(Entity):
    """Relates a parent change with a child change.
    """

# !+VERSION_CLASS_PER_AUDIT_TYPE(mr, apr-2012) review domain+descriptor for 
# versions, how to display a version
class Version(Change):
    """A version (a special kind of change action) of an object and 
    associated change information.
    """
    interface.implements(
        interfaces.IVersion,
    )
    
    @property
    def __name__(self):
        return "ver-%s" % (self.seq)
    
    # !+ should be only for versionable self.head
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    
    # !+VERSION_CLASS_PER_AUDIT_TYPE
    # !+DOCUMENT tmp dummy values to avoid attr errors, etc...
    def __getattr__(self, name):
        print "!+DOCUMENT VERSION->AUDIT...", name, self.audit
        return getattr(self.audit, name)


class Audit(HeadParentedMixin, Entity):
    """Base (abstract) audit record for a document.
    """
    __dynamic_features__ = False
    interface.implements(
        interfaces.IChange # !+IAudit?
    )
    
    @classmethod
    def auditFactory(cls, auditable_cls):
        # Notes:
        # - each "TYPEAudit" class does NOT inherit from the "TYPE" class it audits.
        # - each "TYPEAudit" class inherits from "Audit"
        # - each auditable sub-TYPE gets own dedicated sub-type of "TYPEAudit"
        #   e.g. EventAudit inherits from DocAudit that inherits from Audit.
        # - just as all subtypes of "Doc" are persisted on "doc" table, so are 
        #   all subtypes of "DocAudit" persisted on "doc_audit".
        # 
        # define a subtype of Audit type
        audit_factory_name = "%sAudit" % (auditable_cls.__name__)
        auditable_pk_column = [ c for c in 
            get_mapped_table(auditable_cls).primary_key ][0]
        factory = type(audit_factory_name, (cls,), {
            "head_id_column_name": auditable_pk_column.name })
        # define a subtype of Audit type
        audit_table_name = get_audit_table_name(auditable_cls)
        # Extended properties from cls are inherited... but need to propagate 
        # onto audit_kls any extended properties defined by auditable_cls:
        instrument_extended_properties(factory, audit_table_name, 
            from_class=auditable_cls)
        return factory
    
    head_id_column_name = None # set in cls.auditFactory()
    def audit_head_id():
        doc = "Returns the integer of the single PK of the head object."
        def fget(self):
            return getattr(self, self.head_id_column_name)
        def fset(self, head_id):
            return setattr(self, self.head_id_column_name, head_id)
        return locals()
    audit_head_id = property(**audit_head_id())
    
    # the label is used to for building display labels and/or descriptions of 
    # an audit record, but each type names its "label" attribute differently...
    label_attribute_name = "label"
    @property
    def label(self):
        return getattr(self, self.label_attribute_name)

class DocAudit(Audit):
    """An audit record for a document.
    """
    label_attribute_name = "short_title"
    extended_properties = [
    ]
#instrument_extended_properties(DocAudit, "doc_audit")


class AgendaItem(AdmissibleMixin, Doc):
    """Generic Agenda Item that can be scheduled on a sitting.
    """
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    # !+signatories on AgendaItems?
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    # !+events on AgendaItems?
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
#AgendaItemAudit

class Bill(Doc):
    """Bill domain type.
    """
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
    
    #!+doc_type: default="government", nullable=False,
    
    # !+BILL_MINISTRY(fz, oct-2011) the ministry field here logically means the 
    # bill is presented by the Ministry and so... Ministry should be the author,
    # not a "field" 
    def ministry_id():
        doc = "Related group must be a ministry."
        def fget(self):
            return self.group_id
        def fset(self, ministry_id):
            # !+validate ministry group constraint
            self.group_id = ministry_id
        def fdel(self):
            self.group_id = None
        return locals()
    ministry_id = property(**ministry_id())
    
    @property
    def publication_date(self):
        return self._get_workflow_date("gazetted")

#BillAudit

class Motion(AdmissibleMixin, Doc):
    """Motion domain type.
    """
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
    
    @property
    def notice_date(self):
        return self._get_workflow_date("scheduled")
#MotionAudit

class Question(AdmissibleMixin, Doc):
    """Question domain type.
    """
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
    
    #!+doc_type: default="ordinary", nullable=False,
    #!+response_type: default="oral", nullable=False,
    
    def ministry_id():
        doc = "Related group must be a ministry."
        def fget(self):
            return self.group_id
        def fset(self, ministry_id):
            # !+validate ministry group constraint
            self.group_id = ministry_id
        def fdel(self):
            self.group_id = None
        return locals()
    ministry_id = property(**ministry_id())
    
    @property
    def ministry_submit_date(self):
        return self._get_workflow_date("response_pending")
    
    extended_properties = [
        ("response_type", vp.Text),
        ("response_text", vp.TranslatedText),
    ]
instrument_extended_properties(Question, "doc")

#QuestionAudit

class TabledDocument(AdmissibleMixin, Doc):
    """Tabled document: captures metadata about the document (owner, date, 
    title, description) and can have multiple physical documents attached.
    
    The tabled documents form should have the following:
    - Document title
    - Document link
    - Upload field (s)
    - Document source  / author agency (who is providing the document)
      (=> new table agencies)
    
    - Document submitter (who is submitting the document)
      (a person -> normally mp can be other user)
    
    It must be possible to schedule a tabled document for a sitting.
    """
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
    signatories = one2many("signatories",
        "bungeni.models.domain.SignatoryContainer", "head_id")
    events = one2many("events",
        "bungeni.models.domain.EventContainer", "head_id")
#TabledDocumentAudit


class Event(HeadParentedMixin, Doc):
    """Base class for an event on a document.
    """
    #!+parliament_id is (has always been) left null for events, how best to 
    # handle this, possible related constraint e.g. head_id must NOT be null, 
    # validation, ... ?
    __dynamic_features__ = True
    
    # !+alchemist properties not inherited, must be re-instrumented on class
    files = one2many("files",
        "bungeni.models.domain.AttachmentContainer", "head_id")
#EventAudit


class Attachment(HeadParentedMixin, Entity):
    """A file attachment to a document. 
    """
    __dynamic_features__ = True # !+ should be False?
    interface.implements(
        interfaces.IDocument, # !+IDoc?
        interfaces.IAttachment,
        ore.xapian.interfaces.IIndexable, # !+bungeni_custom
    )
    
    # the owner of the "owning" item
    @property
    def owner_id(self):
        return self.head.owner_id
    
    @property
    def owner(self):
        return self.head.owner

class AttachmentAudit(Audit):
    """An audit record for an attachment.
    """
    label_attribute_name = "title"
    
    # !+VERSION_CLASS_PER_AUDIT_TYPE?
    @property # !+TMP workaround erros
    def short_title(self):
        print "!+AttachmentAudit... short_title -> title", self.title, self
        return self.title
    @property # !+TMP
    def long_title(self):
        print "!+AttachmentAudit... long_title -> title", self.title, self
        return self.title
    @property # !+TMP
    def body(self):
        print "!+AttachmentAudit... body -> description", self.description, self
        return self.title


class Heading(Entity):
    """A heading in a report.
    """
    interface.implements(interfaces.ITranslatable, interfaces.IScheduleText)
    __dynamic_features__ = False
    
    type = "heading"
    
    @property
    def status_date(self):
        return None

# auditable (by default), but not a Doc
class Signatory(Entity):
    """Signatory for a Bill or Motion or other doc.
    """
    interface.implements(
        interfaces.IBungeniContent,
        interfaces.IDocument, # !+IDoc?
    )
    
    __dynamic_features__ = True
    
    @property
    def owner_id(self):
        return self.user_id
    
    @property
    def owner(self):
        return self.user

class SignatoryAudit(Audit):
    """An audit record for a signatory.
    """
    label_attribute_name = None
    @property
    def label(self):
        return self.user.fullname
    description = label

    @property
    def user(self):
        return self.audit_head.user

#############

class ParliamentSession(Entity):
    """
    """
    sort_on = ["start_date", ]
    sort_dir = "desc"
    interface.implements(interfaces.ITranslatable)


class ObjectSubscriptions(object):
    """
    """

# ###############

class Constituency(Entity):
    """A locality region, which elects an MP.
    """
    cdetail = one2many("cdetail",
        "bungeni.models.domain.ConstituencyDetailContainer", "constituency_id")
    parliamentmembers = one2many("parliamentmembers",
        "bungeni.models.domain.MemberOfParliamentContainer", "constituency_id")
    #sort_replace = {"province_id": ["province"], "region_id": ["region"]}
    interface.implements(interfaces.ITranslatable)


class Region(Entity):
    """Region of the constituency.
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
    """Country of Birth.
    """
    pass

class ConstituencyDetail(object):
    """Details of the Constituency like population and voters at a given time.
    """
    pass


# ##########


class TitleType(object):
    """Types of titles in groups
    """
    interface.implements(interfaces.ITitleType, interfaces.ITranslatable)


class MemberTitle(Entity):
    """The role title a member has in a specific context and one 
    official address for a official role.
    """
    interface.implements(interfaces.ITranslatable)


class MinistryInParliament(object):
    """Auxilliary class to get the parliament and government for a ministry.
    """


class EditorialNote(Entity):
    """Arbitrary text inserted into schedule
    """
    type = u"editorial_note"
    interface.implements(interfaces.ITranslatable, interfaces.IScheduleText)

class ItemSchedule(Entity):
    """For which sitting was a parliamentary item scheduled.
    """
    discussions = one2many("discussions",
        "bungeni.models.domain.ItemScheduleDiscussionContainer", "schedule_id")

    def get_item_domain(self):
        domain_class = None
        try:
            domain_class = capi.get_type_info(self.item_type).domain_model
        except KeyError:
            #!+TYPE REGISTRY(mb, mar-2012) Try to lookup via workflow
            # demo data not synced with polymorphic prop changes in trunk@r9135
            log.debug("Unable to locate type %s from type info lookup." 
                "Trying workflow lookup.", self.item_type
            )
            for type_key, type_info in capi.iter_type_info():
                if (type_info.workflow and 
                    (type_info.workflow.name == self.item_type)
                ):
                    domain_class = type_info.domain_model
                    break
        if domain_class is None:
            log.error("Unable to locate domain  class for item of type %s",
                self.item_type
            )
        return domain_class

    def _get_item(self):
        """Query for scheduled item by type and ORM mapped primary key
        """
        domain_class = self.get_item_domain()
        if domain_class is None:
            return None
        item = Session().query(domain_class).get(self.item_id)
        item.__parent__ = self
        return item

    def _set_item(self, schedule_item):
        self.item_id = get_mapped_object_id(schedule_item)
        self.item_type = schedule_item.type

    item = property(_get_item, _set_item)
    
    sort_on = ["planned_order", ]
    sort_dir = "asc"

class ItemScheduleDiscussion(Entity):
    """A discussion on a scheduled item.
    """
    interface.implements(interfaces.ITranslatable)


class HoliDay(object):
    """Is this day a holiday?
    if a date in in the table it is otherwise not
    """

''' !+BookedResources
class Resource (object):
    """A Resource that can be assigned to a sitting.
    """

class ResourceBooking (object):
    """Assign a resource to a sitting.
    """
class ResourceType(object):
    """A Type of resource.
    """
'''

class Venue(Entity):
    """A venue for a sitting.
    """
    interface.implements(interfaces.ITranslatable, interfaces.IVenue)


class Report(Doc):
    """Agendas and minutes.
    """
    interface.implements(interfaces.ITranslatable)
    sort_on = ["end_date"] + Doc.sort_on

# !+SITTING_REPORT(mr, apr-2011) why does SittingReport (mapped as an 
# association type, and not a Doc in any way) inherit from Report?!
class SittingReport(Report):
    """Which reports are created for this sitting.
    """

# !+Report4Sitting((mr, apr-2012) naming!
class Report4Sitting(Report):
    """Display reports for a sitting.
    """


class ObjectTranslation(object):
    """Get the translations for an Object.
    """


''' !+TYPES_CUSTOM

#####################
# DB vocabularies
######################

class QuestionType(Entity):
    """Question type
    """
    interface.implements(interfaces.ITranslatable, interfaces.IQuestionType)

class ResponseType(Entity):
    """Response type
    """
    interface.implements(interfaces.ITranslatable, interfaces.IResponseType)

class MemberElectionType(Entity):
    """Member election type
    """
    interface.implements(interfaces.ITranslatable, 
        interfaces.IMemberElectionType
    )

class AddressType(Entity):
    """Address Types.
    """
    interface.implements(interfaces.ITranslatable, 
        interfaces.IAddressType
    )
class PostalAddressType(Entity):
    """Postal address type
    """
    interface.implements(interfaces.ITranslatable, 
        interfaces.IPostalAddressType
    )

class CommitteeTypeStatus(Entity):
    """Committee type status
    """
    interface.implements(interfaces.ITranslatable,
        interfaces.ICommitteeTypeStatus
    )
'''
