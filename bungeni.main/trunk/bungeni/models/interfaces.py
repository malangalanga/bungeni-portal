# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni domain model interfaces

Bungeni-specific model interfaces, exclusively dedicated for Bungeni use, 
and applying to any target type is the sole responsibility of Bungeni.

A domain model may define a dedicated conventionally-named interface and then
use that interface as desired by the bungeni application e.g. for registering 
components.

Each interface here should never be modified by 3rd party code or other 
processes in any way e.g. by catalyst.

$Id$
"""
log = __import__("logging").getLogger("bungeni.models.interfaces")

from zope import interface, schema
from zope.app.container.interfaces import IContainer
from zope.configuration.fields import MessageID
from ore.wsgiapp.interfaces import IApplication

from bungeni.alchemist.interfaces import IAlchemistContainer
from bungeni import _


DEBUG = True
ENABLE_LOGGING = False
ENABLE_EVENT_LOGGING = False

if ENABLE_EVENT_LOGGING:
    import eventlog


class IBungeniApplication(IApplication):
    """Bungeni Application.
    """




class IBungeniAdmin(IContainer):
    """Admin Container.
    """
class IAdminUserContainer(interface.Interface):
    """A container that returns object for the admin ui, marked with 
    admin interface markers.
    """
''' !+UNUSED(mr, nov-2010)
class IAdminGroupContainer(interface.Interface):
    pass
'''

class IUserAdmin(interface.Interface):
    """Marker interface attached to user objects viewed in the admin for 
    admin views.
    """

class IGroupAdmin(interface.Interface):
    """Marker interface attached to user objects viewed in the admin for 
    admin views.
    """

# !+NAMING(mr, apr-2011) rename IUser, inconsistent with domain
class IBungeniUser(interface.Interface):
    """A user in bungeni.
    """
IUser = IBungeniUser
class IUserContainer(IAlchemistContainer): pass

class IGroup(interface.Interface):
    """A group in bungeni.
    """


class IBungeniContainer(IAlchemistContainer):
    """Parliamentary container.
    """

class IGroupMember(interface.Interface):
    """Group membership in bungeni.
    """
class IGroupMemberContainer(IBungeniContainer): pass


# !+CUSTOM
class ILegislature(IGroup): pass
class IChamber(IGroup): pass
class IMember(IGroupMember): pass
# /!+CUSTOM


class IMemberRole(interface.Interface):
    """Group membership sub roles in bungeni.
    """
class IMemberRoleContainer(IBungeniContainer): pass

class IDocPrincipal(interface.Interface): pass

class IGroupAssignment(IDocPrincipal):
    """Doc group assignment.
    """
class IGroupAssignmentContainer(IBungeniContainer): pass


class IDrafted(interface.Interface):
    """Object supports having an "drafter" i.e. a drafter:user attribute.
    """
    def drafter():
        """Get the user instance that is the drafter of this item i.e. the user 
        that has been assigned "bungeni.Drafter" role on this item.
        """

class IOwned(IDrafted):
    """Object supports having an "owner" i.e. an owner:principal attribute.
    """
    def owner():
        """Get the user instance that is the owner of this item i.e. the 
        principal (user or group) that has been assigned the "bungeni.Owner" 
        role on this item.
        """

class ISerializable(interface.Interface):
    """Marker interface for serializable types"""

class IBungeniContent(interface.Interface):
    """Marker for Bungeni Content (all documents, not only legislative).
    
    Note the distinctions of the (current and intended) usage of the 
    following related domain interfaces:
    
    IAlchemistContent:
        all "bungeni content", for use by the autogeneration of
        schemas/interfaces derived from rdb defns
        !+IBungeniContent merge
    IBungeniContent
        all documents, not only legislative
        !+IBungeniContent generalize to imply "all bungeni content" (thus
        becoming equivalent to IAlchemistContent) and merge, 
        standardize all registrations on the appropriate one
    IDoc:
        dedicated interface of the Doc system archetype (inherited also by
        sub-archetypes i.e. Event)
    ILegislativeContent:
        true legislative (legal) content
    """
    # !+ schema attributes ?
    # status: sa.Unicode(48)
    # status_date: sa.DateTime(timezone=False)

class IDoc(IBungeniContent):
    """Doc - dedicated interface.
    """

class ILegislativeContent(IBungeniContent):
    """Marker interface for true legislative (legal) content.
    """


class ISittingContainer(IBungeniContainer): pass

class IVersion(interface.Interface):
    """A version of an object is identical in attributes to the actual 
    object, based on that object's domain schema.
    """
class IDocVersion(IVersion):
    """A version of a Doc instance.
    """

# !+AuditLogView(mr, nov-2011)
#class IChangeContainer(IBungeniContainer): pass


class IHeading(interface.Interface): pass
class IHeadingContainer(IAlchemistContainer): pass

class IEvent(IBungeniContent): pass
class IEventContainer(IBungeniContainer): pass


# !+IITEMVersion(mr, sep-2011): should IITEMVersion exist at all? if so, 
# should it inherit from IITEM, or from IVersion? Note that 
# IITEMVersionContainer inherits from IVersionContainer (is used by alchemist).


class ISitting(interface.Interface): pass
class ISittingReport(interface.Interface): pass

class ISittingAttendance(interface.Interface): pass
class ISittingAttendanceContainer(IAlchemistContainer): pass
    
class IItemSchedule(interface.Interface): pass
class IItemScheduleContainer(IAlchemistContainer): pass

class IEditorialNote(interface.Interface):
    """Marker interface for editorial notes in a sitting's agenda"""
class IEditorialNoteContainer(IAlchemistContainer): pass

class IAgendaTextRecord(interface.Interface):
    """Marker interface for agenda text records in a sitting's agenda"""

class IScheduleText(interface.Interface):
    """Marker interface for text records e.g. in agenda.
    This covers `IHeading` and `IEditorialNote'` and `IAgendaTextRecord` at 
    this point.
    """

class IScheduleContent(interface.Interface):
    """Marker interface for content that may be managed in scheduling
    """

class IItemScheduleDiscussion(interface.Interface): pass
class IItemScheduleDiscussionContainer(IAlchemistContainer): pass

class IItemScheduleVote(interface.Interface): pass
class IItemScheduleVoteContainer(IAlchemistContainer): pass


class ISession(interface.Interface): pass
class ISessionContainer(IAlchemistContainer): pass

class IBungeniSetup(interface.Interface):

    def setUp(app):
        """Setup the application on server start.
        """

class IBungeniRegistrySettings(interface.Interface):

    global_number = schema.Bool(
        title=_(u"Reset global registry number"),
        default=False
    )
    questions_number = schema.Bool(
        title=_(u"Reset questions registry number"),
        default=False
    )
    motions_number = schema.Bool(
        title=_(u"Reset motions registry number"),
        default=False
    )
    agendaitems_number = schema.Bool(
        title=_(u"Reset agenda items registry number"),
        default=False
    )
    bills_number = schema.Bool(
        title=_(u"Reset bills registry number"),
        default=False
    )
    reports_number = schema.Bool(
        title=_(u"Reset reports registry number"),
        default=False
    )
    tableddocuments_number = schema.Bool(
        title=_(u"Reset tabled documents registry number"),
        default=False
    )
    
    

class IBungeniUserSettings(interface.Interface):

    # examples
    email_delivery = schema.Bool(
        title=_(u"Email Notifications Enabled?"),
        default=True
    )

class IBungeniEmailSettings(interface.Interface):
    hostname = schema.TextLine(
        title = _("Email server hostname or IP address"),
        default = u"localhost",
    )
    port = schema.Int(
        title = _("Email server port"),
        default = 25,
    )
    username = schema.TextLine(
        title = _("Email server login name"),
        default = u"",
    )
    password = schema.Password(
        title = _("Email server password"),
        default = u"",
    )
    default_sender = schema.TextLine(
        title = _("Default sender address"),
        default = u"",
    )
    use_tls = schema.Bool(
        title = _("Connect securely to mail server (using TLS)"),
        default = False,
    )

class ISearchSettings(interface.Interface):
    search_uri = schema.TextLine(
        title=_("Full URL to eXist REST search."),
        default=u"http://localhost:8088/exist/restxq/ontology_bungeni"
    )

class IAttachment(interface.Interface): pass
class IAttachmentContainer(IAlchemistContainer): pass
# !+VERSION_CLASS_PER_TYPE
class IAttachedFileVersion(interface.Interface): pass 


class ISignatory(interface.Interface):
    """Signatories for bills, motions, ...
    """
class ISignatoryContainer(IAlchemistContainer): pass




class IDirectoryLocation(interface.Interface):

    repo_path = schema.ASCIILine()
    object_id = schema.Int()
    object_type = schema.ASCIILine()


class IProxiedDirectory(interface.Interface):
    """An interface for a contained directory we can attach menu links
    to that point back to our parent.
    """


class IChange(interface.Interface):
    """Marker for Change (log table).
    """

class IMemberTitle(interface.Interface):
    """Marker for member titles"""
class IMemberTitleContainer(IAlchemistContainer): pass

class ITitleType(interface.Interface):
    """Title types"""
class ITitleTypeContainer(IAlchemistContainer): pass

class IAddress(interface.Interface):
    """Base marker interface for an Address
    """
class IAddressContainer(IAlchemistContainer): pass
class IGroupAddress(IAddress):
    """Marker interface addresses of a group.
    """
class IGroupAddressContainer(IAlchemistContainer): pass
class IUserAddress(IAddress):
    """Marker interface addresses of a user.
    """
class IUserAddressContainer(IAlchemistContainer): pass

class IReport(IBungeniContent): pass
class IReportContainer(IAlchemistContainer): pass

class IUserDelegation(interface.Interface): pass
class IUserDelegationContainer(IAlchemistContainer): pass

class ITranslatable(interface.Interface):
    """Marker Interface if an object is translatable.
    """
    language = interface.Attribute("The language of the values of the "
        "translatable attributes of the instance")

class IBungeniVocabulary(interface.Interface):
    """Marker interface for vocabularies managed in admin UI."""


class IVenue(IBungeniVocabulary):
    """Marker interface for venues vocabulary"""
class IVenueContainer(IAlchemistContainer): pass


class ISubRoleDirective(interface.Interface):
    """Define a new sub role."""
    id = schema.Id(
        title=u"Id",
        description=u"Id as which this object will be known and used.",
        required=True)

    title = MessageID(
        title=u"Title",
        description=u"Provides a title for the object.",
        required=True)

    description = MessageID(
        title=u"Description",
        description=u"Provides a description for the object.",
        required=False)
        
    role = schema.Id(
        title=u"Parent Role ID",
        description=u"Role ID for role which this subrole extends",
        required=True)

class ISubRoleAnnotations(interface.Interface):
    sub_roles = interface.Attribute("sub_roles")
    is_sub_role = interface.Attribute("is_sub_role")
    parent = interface.Attribute("parent")

class ICountry(interface.Interface):
    """Marker interface for Country"""


class IDebateRecord(interface.Interface):
    """Marker interface for debate records"""

class IDebateRecordItem(interface.Interface):
    """Marker interface for debate record items"""

class IDebateDoc(interface.Interface):
    """Marker interface for docs debated in a sitting"""

class IDebateSpeech(interface.Interface):
    """Marker interface for debate speeches"""

class IDebateMedia(interface.Interface):
    """Marker interface for debate record media"""

class IDebateMediaContainer(IAlchemistContainer):
    """Interface for debate media container"""

class IDebateTake(interface.Interface):
    """Marker interface for debate take"""

class IDebateTakeContainer(IAlchemistContainer):
    """Marker interface for debate takes container"""


# OAuth
class IOAuthApplication(interface.Interface):
    """Marker interface for an OAuth Application record"""

class IOAuthApplicationContainer(IAlchemistContainer):
    """Marker interface for an OAuth Applications container"""

class IOAuthAuthorization(interface.Interface):
    """Marker interfeace for OAuth authorizations"""

class IOAuthAuthorizationToken(interface.Interface):
    """Marker interface for OAuth authorization token"""

class IOAuthAccessToken(interface.Interface):
    """Marker interface for OAuth access token"""


