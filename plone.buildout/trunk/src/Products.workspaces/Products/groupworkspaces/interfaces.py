from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IGroupWorkspacesView(Interface):
    """Marker interface identifying the Groups Workspace View'
    """

class IMembershipView(Interface):
    """Browser view for the Members (membership) folder.
    """

    def member_folders():
        """
        Returns a sorted listing of members.
        """

    def alphabetise():
        """
        Returns an alphabetised dictionary of member names.
        """
    
