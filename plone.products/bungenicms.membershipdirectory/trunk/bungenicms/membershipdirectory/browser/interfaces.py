from plonetheme.classic.browser.interfaces import IThemeSpecific as IClassicTheme
from zope.interface import Interface

class IMemberProfileBrowser(Interface):
    """
    Allows registration of a single browser view for folderish legislator items
    """
    
class IThemeSpecific(IClassicTheme):
    """Marker interface that defines a Zope 3 browser layer.
    """
