from plonetheme.classic.browser.interfaces import IThemeSpecific as IClassicTheme
from zope.interface import Interface

from collective.documentviewer.interfaces import IGlobalDocumentViewerSettings
from collective.documentviewer.interfaces import ILayer as IDocumentViewerLayer
from zope import schema
from zope.interface import implements

class IRepositoryItemBrowser(Interface):
    """
    Allows registration of a single browser view for folderish repository items
    """
    
class IThemeSpecific(IClassicTheme):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ICustomLayer(IDocumentViewerLayer):
    """
    custom layer class
    """
    
class IEnhancedDocumentViewerSchema(IGlobalDocumentViewerSettings):
    """ 
    Use all the fields from the default schema, and add various extra fields.
    """
    
    folder_location = schema.TextLine(
        title=u"Default folder location",
        description=u'A bungenicms.repository feature. This folder will be created in the Plone root folder. '
                    u'It will be the final place where the newly converted attachment files from the RepositoryItem are stored.',
        default=u"files-folder")
