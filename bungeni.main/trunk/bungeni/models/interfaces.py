# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni domain model interfaces

Bungeni-specific model interfaces, exclusively dedicated for Bungeni use, 
and applying to any target arget type is the sole responsibility of Bungeni.

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
from bungeni.alchemist.interfaces import IAlchemistContainer
from ore.wsgiapp.interfaces import IApplication
from i18n import _
from zope.configuration.fields import MessageID

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

class IGroup(interface.Interface):
    """A group in bungeni.
    """
class IUserContainer(IAlchemistContainer): pass


class IBungeniContainer(IAlchemistContainer):
    """Parliamentary container.
    """

class IChamber(IGroup):
    """Marker interface for parliament chamber group.
    """
class IChamberContainer(IAlchemistContainer): pass

class IGovernment(IGroup):
    """Marker interface for group Government.
    """
class IGovernmentContainer(IAlchemistContainer): pass

class IMinistry(IGroup):
    """Marker interface for group ministry """
class IMinistryContainer(IAlchemistContainer): pass

class ICommittee(IGroup):
    """Marker interface for committees.
    """
class ICommitteeContainer(IAlchemistContainer): pass

class IJointCommittee(ICommittee):
    """Marker interface for joint committee.
    """
class IJointCommitteeContainer(ICommitteeContainer): pass

class IPoliticalGroup(IGroup):
    """Marker interface for political group (inside parliament).
    """
class IPoliticalGroupContainer(IAlchemistContainer): pass

class IOffice(IGroup):
    """Marker interface for a parliamentary office.
    """
class IOfficeContainer(IAlchemistContainer): pass

class ICommittee(IGroup): pass
class ICommitteeContainer(IAlchemistContainer): pass


class IGroupMember(interface.Interface):
    """Group membership in bungeni.
    """
class IGroupMemberContainer(IBungeniContainer): pass

class IGroupMemberRole(interface.Interface):
    """Group membership sub roles in bungeni.
    """
class IGroupMemberRoleContainer(IBungeniContainer): pass

class IGroupDocumentAssignment(interface.Interface):
    """Group document assigment.
    """
class IGroupDocumentAssignmentContainer(IBungeniContainer): pass

class IMember(IGroupMember): pass
class IMemberContainer(IGroupMemberContainer): pass

class IPoliticalGroupMember(IGroupMember): pass
class IPoliticalGroupMemberContainer(IGroupMemberContainer): pass

class IMinister(IGroupMember): pass
class IMinisterContainer(IGroupMemberContainer): pass

class ICommitteeMember(IGroupMember): pass
class ICommitteeMemberContainer(IGroupMemberContainer): pass

class ICommitteeStaff(IGroupMember): pass
class ICommitteeStaffContainer(IGroupMemberContainer): pass

class IOfficeMember(IGroupMember): pass
class IOfficeMemberContainer(IAlchemistContainer): pass

class IOwned(interface.Interface):
    """Object supports having an "owner" i.e. an owner:user attribute.
    """
    def owner():
        """Get the user instance that is the owner of this item.
        """

class ISerializable(interface.Interface):
    """Marker interface for serializable types"""

class IBungeniContent(IOwned):
    """Parliamentary content
    !+IAlchemistContent merge?
    
    !+IBungeniContent(mr, nov-2011) clarify distinction, 
    in intention and use, between the following interfaces: 
    IBungeniParliamentaryContent -> IBungeniContent -> IAlchemistContent
    Should standardize registration on the appropriate one (or on IWorklfowed).
    """
    # !+ schema attributes ?
    # status: sa.Unicode(48)
    # status_date: sa.DateTime(timezone=False)

class IBungeniParliamentaryContent(IBungeniContent):
    """Marker interface for true bungeni parliamentary content"""
    # !+IBungeniContent(mr, may-2012) drop either IBungeniContent or
    # IBungeniParliamentaryContent !

class ISittingContainer(IBungeniContainer): pass

class IVersion(interface.Interface):
    """A version of an object is identical in attributes to the actual 
    object, based on that object's domain schema.
    """
class IDocVersion(IVersion):
    """A version of a Doc instance.
    """

''' !+OBSOLETE_VERSIONING
class IVersionContainer(IBungeniContainer):
    pass
'''
# !+AuditLogView(mr, nov-2011)
#class IChangeContainer(IBungeniContainer): pass


class IHeading(interface.Interface): pass
class IHeadingContainer(IAlchemistContainer): pass

class IEvent(IBungeniContent): pass
class IEventContainer(IBungeniContainer): pass


# !+IITEMVersion(mr, sep-2011): should IITEMVersion exist at all? if so, 
# should it inherit from IITEM, or from IVersion? Note that 
# IITEMVersionContainer inherits from IVersionContainer (is used by alchemist).

class IDoc(IBungeniContent):
    """Doc - dedicated interface.
    """

# !+IBungeniParliamentaryContent clean out deteriorated usage, clarify 
# intention for these two as well as IBungeniContent, get rid of at least one
def is_legal_doc(context):
    # doc (but not event) types are legal documents
    return IDoc.providedBy(context) and not IEvent.providedBy(context)


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


class IAgendaItem(IBungeniContent): pass
class IAgendaItemContainer(IBungeniContainer): pass
# !+IITEMVersion
#class IAgendaItemVersion(IAgendaItem): pass
#!+OBSOLETE_VERSIONING class IAgendaItemVersionContainer(IVersionContainer): pass

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

class IAttachment(IOwned): pass
class IAttachmentContainer(IAlchemistContainer): pass
# !+VERSION_CLASS_PER_TYPE
class IAttachedFileVersion(interface.Interface): pass 
# !+OBSOLETE_VERSIONING
#class IAttachedFileVersionContainer(IVersionContainer): pass

class ISignatory(interface.Interface):
    """Signatories for bills, motions, ...
    """
class ISignatoryContainer(IAlchemistContainer): pass

class ISignatoryManager(interface.Interface):
    """Validation machinery for iterms with signatories"""

    signatories = interface.Attribute("""signatories iteratable""")
    
    min_signatories = interface.Attribute("""minimum consented signatories""")

    max_signatories = interface.Attribute("""maximum consented signatories""")

    signatories_count = interface.Attribute("""number of signatories""")
    
    consented_signatories = interface.Attribute("""number of consented """)
    
    # !+naming(mr, oct-2011) please follow standard python naming conventions!
    
    def validate_signatories():
        """Validate signatories count on parliamentary item i.e. number added
        """

    def require_signatures():
        """Does the document or object require signatures
        """

    def validate_consented_signatories():
        """Validate number of consented signatories against min and max
        """

    def allow_signature():
        """Check that the current user has the right to consent on document 
        """
    
    def document_submitted():
        """Check that the document has been submitted
        """
    
    def document_is_draft():
        """Check that the document is in draft stage
        """
    
    def expire_signatures():
        """Should pending signatures be archived
        """
    
    def update_signatories():
        """Fire any workflow transitions within current state.
        This should update all signatures depending on parent document state.
        """

    def setup_roles():
        """Set local signatories/owner roles on document and signature
        objects.
        """

    def fire_workflow_actions():
        """Fire off any changes after workflow change on parent document"""

class ISchedulingManager(interface.Interface):
    """Configurator for class implementing scheduling feature
    """
    schedulable_states = interface.Attribute("""object's schedulable states""")
    scheduled_states = interface.Attribute("""object's scheduled states""")

class IDirectoryLocation(interface.Interface):

    repo_path = schema.ASCIILine()
    object_id = schema.Int()
    object_type = schema.ASCIILine()

class IProxiedDirectory(interface.Interface):
    """An interface for a contained directory we can attach menu links
    to that point back to our parent.
    """

# IFeature marker interfaces -- apply to a domain model, to declare that it 
# implements the feature. To avoid "english language anomalies of derived names" 
# e.g "schedule" -> ISchedulable, adopt a very KISS feature->interface naming 
# convention: "schedule"->IFeatureSchedule

class IFeature(interface.Interface):
    """Base feature marker interface.
    """
class IFeatureAudit(IFeature):
    """Marks support for "audit" feature.
    """
class IFeatureVersion(IFeature):
    """Marks support for "version" feature (requires "audit").
    """
class IFeatureAttachment(IFeature):
    """Marks support for "attachment" feature.
    """
class IFeatureEvent(IFeature):
    """Marks support for "event" feature.
    """
class IFeatureSignatory(IFeature):
    """Marks support for "signatory" feature.
    """
class IFeatureSchedule(IFeature):
    """A document can be scheduled: support for the "schedule" feature.
    """
class IFeatureSitting(IFeature):
    """A group can hold sittings: support for the "sitting" feature.
    """
class IFeatureAddress(IFeature):
    """Can have addresses: support for the "address" feature.
    """
class IFeatureWorkspace(IFeature):
    """Marks support for "workspace" feature.
    """
class IFeatureNotification(IFeature):
    """Marks support for "notification" feature.
    """
class IFeatureEmail(IFeature):
    """Marks support for "email" notifications feature.
    """
class IFeatureDownload(IFeature):
    """Marker for classes supporting "download" feature".
    """
class IFeatureUserAssignment(IFeature):
    """Marks support for "user assignment" feature
    """
class IFeatureGroupAssignment(IFeature):
    """Marks support for "group assignment" feature
    """
#

DOWNLOAD_TYPES = [
    ("pdf", _("as pdf")),
    ("odt", _("as open document")),
    ("doc", _("as MS Word")),
    ("docx", _("as MS Word 2007+")),
    ("txt", _("as text")),
    ("rtf", _("as rich text")),
    ("htm", _("as html")),
]
DOWNLOAD_TYPE_KEYS = [ k for k,v in DOWNLOAD_TYPES]
def validate_download_types(obj):
    assert set(obj.allowed_types).issubset(DOWNLOAD_TYPE_KEYS), \
        ("allowed download types:  %s. you entered: %s" 
            %(", ".join(DOWNLOAD_TYPE_KEYS),
                ", ".join(obj.allowed_types)))

class IDownloadManager(interface.Interface):
    """schema for download manager config adapters"""
    allowed_types = interface.Attribute("""allowed download types""")

    interface.invariant(validate_download_types)
    
    def get_allowed_types():
        """get a subset of DOWNLOAD_TYPES"""
    
''' !+DATERANGEFILTER(mr, dec-2010) disabled until intention is understood
class IDateRangeFilter(interface.Interface):
    """Adapts a model container instance and a SQLAlchemy query
    object, applies a date range filter and returns a query.

    Parameters: ``start_date``, ``end_date``.

    These must be bound before the query is executed.
    """
'''


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
    sub_roles = interface.Attribute('sub_roles')
    is_sub_role = interface.Attribute('is_sub_role')
    parent = interface.Attribute('parent')

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
