from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from ploned.ui.interfaces import IPlonedSkin
from ore.yui.interfaces import IYUILayer
from bungeni.rest.interfaces import IRESTLayer

from zope.configuration import fields
from zope import schema
from zope.viewlet.interfaces import IViewletManager
class IBungeniSkin(IPlonedSkin, IYUILayer):
    """Bungeni application skin."""
class IBungeniAuthenticatedSkin(IBungeniSkin):
    """Skin for authenticated users."""
class IBungeniRESTSkin(IRESTLayer):
    """Bungeni REST skin."""

from zope import interface
class IWorkspaceContainer(interface.Interface):
    """Marker for a domain object that is also a user's workspace container."""
class IWorkspaceSectionContext(interface.Interface):
    """Marker for a section of a workspace."""
class IWorkspacePIContext(IWorkspaceSectionContext):
    """Marker for the PI section of a workspace."""
class IWorkspaceMIContext(IWorkspaceSectionContext):
    """Marker for the MI section of a workspace."""
class IWorkspaceArchiveContext(IWorkspaceSectionContext):
    """Marker for the Archive section of a workspace."""

class IWorkspacePlenaryContainer(interface.Interface):
    """Marker for a domain object that is also a user's workspace container."""

class IWorkspaceSchedulingContainer(interface.Interface):
    """Marker"""
class IWorkspaceCommitteeSchedulingContainer(interface.Interface):
    """Marker"""
class ISpeakerWorkspace(IBrowserView):
    """Speaker's workspace."""
class IClerkWorkspace(IBrowserView):
    """Clerk's workspace."""
class IAdministratorWorkspace(IBrowserView): # !+ remove out
    """Administrator's workspace."""
class IMinisterWorkspace(IBrowserView):
    """Minister's workspace."""
class IMPWorkspace(IBrowserView):
    """MP's workspace."""


class IHomePageLayer(IDefaultBrowserLayer):
    """Requests for the Home Page."""
class IResourceNonLayer(interface.Interface):
    """A fake layer, to mark that the request is for some resource"""
class IFormEditLayer(interface.Interface):
    """Views showing a Form in edit mode."""

class IRSSRepresentationLayer(IDefaultBrowserLayer):
    """ Requests for rss representation of
        some objects
    """

class IAnonymousSectionLayer(IDefaultBrowserLayer):
    """Requests within a section that should return always same public-only 
    information irrespective of who is logged in (or not). 
    """

class IArchiveSectionLayer(IAnonymousSectionLayer):
    """Requests for an object within the archive."""

class IBusinessSectionLayer(IAnonymousSectionLayer, IRSSRepresentationLayer):
    """Requests for an object within the business section."""
class IBusinessWhatsOnSectionLayer(IAnonymousSectionLayer):
    """Requests for an object within the whats on page of the business section."""

class IPermalinkSectionLayer(IBusinessSectionLayer):
    """Requests for an object within the bungeni section."""

class IMembersSectionLayer(IAnonymousSectionLayer):
    """Requests for an object within the members section."""

class IWorkspaceOrAdminSectionLayer(IDefaultBrowserLayer):
    """Requests for an object within the workspace OR admin section."""
class IAdminSectionLayer(IWorkspaceOrAdminSectionLayer):
    """Requests for an object within the admin section."""
class IWorkspaceSectionLayer(IWorkspaceOrAdminSectionLayer):
    """Requests for an object within the workspace section."""
class IWorkspaceSchedulingSectionLayer(IWorkspaceOrAdminSectionLayer):
    """Requests for an object within the scheduling section."""
class IFeedViewletManager(IViewletManager):
    """Viewlet manager for feed links"""
    
class IOpenOfficeConfig(interface.Interface):
    def getPath():
        "Path to the Openoffice Python binary"
    def getPort():
        "Port on which Openoffice is running"
    def getMaxConnections():
        "Maximum number of simultaneous connections"
        
class IOpenOfficeConfigSchema(interface.Interface):
    path = fields.Path(
        title=u"UNO Python Path",
        description=u"This is the path to UNO enabled Python",
        required=True
        )
    port = schema.Int(
        title=u"OpenOffice.org Port",
        description=u"Port on which OpenOffice is running",
        required=True,
        default=2002
        )
    maxConnections = schema.Int(
        title=u"Max Connectiond",
        description=u"Maximum number of simultaneous connections to OpenOffice",
        required=True,
        default=5
        )

class IGenenerateVocabularyDefault(interface.Interface):
    """Generate default value for vocabulary"""
    
    def getDefaultVocabularyValue():
        "Get the default value in vocabulary"


class ITreeVocabulary(interface.Interface):
    """ Generate tree vocabulary as JSON data.
        Also provides a validation of values
    """

    def generateJSON():
        "Generate JSON data from vocabulary "

    def getTermById(value):
        "Gets the vocabulary term or None"

    def validateTerms(value_list):
        "validate a list of vocabulary terms"

class IVocabularyTextField(schema.interfaces.IText):
    """Text field supporting vocabulary """
    vocabulary = interface.Attribute("A vocabulary")
