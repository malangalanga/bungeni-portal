from zope import interface, schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.interfaces import IViewletManager
from z3c.menu.ready2go import interfaces as imenu

from zope.interface import directlyProvides
from zope.browsermenu.interfaces import IMenuItemType
from zope.contentprovider.interfaces import IContentProvider

class IPlonedSkin( IDefaultBrowserLayer ):
    """ plone skin for zope3  """

class IStructuralView(IBrowserView):
    """Marker-interface for views that are structural in the sense
    that they do provide content actions, but they are still content
    views on some object."""

class ICSSManager( IViewletManager ):
    """ viewlet manager for css """

class IJavaScriptManager( IViewletManager ):
    """ viewlet manager for js """

class ILeftColumnManager( IViewletManager ):
    """ """

class IRightColumnManager( IViewletManager ):
    """ """

class IAboveContentManager( IViewletManager ):
    """ """

class IBelowContentManager( IViewletManager ):
    """ """

class IContentViewsManager( IViewletManager ):
    """ """

class IPortalHeaderManager( IViewletManager ):
    """ """
    
class IPortalToolsManager( IViewletManager ):
    """ """
    
class IPortalFooterManager( IViewletManager ):
    """ """

class IPersonalBarMenu( imenu.IMenuManager ):
    """ personalized site actions, login, logout, dashboard"""
    
class IPersonalTasksMenu( imenu.IMenuManager ):
    """ personalized site actions, login, logout, dashboard"""

class IPersonalActionItem( imenu.ISiteMenuItem ):
    """ we register various role required """
    groups = schema.List( value_type=schema.Int() )
    roles = schema.List( value_type=schema.Int() )

class IContentViews( IViewletManager ):
    """ """

class IDocumentActions( IViewletManager ):
    """ """

class ISkinDirectory( interface.Interface ):
    """ a skin directory looks up resources in a stacked lookup through across layers """
    layers = schema.List( value_type=schema.Object( interface.Interface ) )

class IContentMenuView(IContentProvider):
    """The view that powers the content menu

    This will construct a menu by finding an adapter to IContentMenu.
    """

    def available():
        """Determine whether the menu should be displayed at all.
        """

    def menu():
        """Create a list of dicts that can be used to render a menu.

        The keys in this dict are: title, description, action (a URL),
        selected (a boolean), icon (a URI), extra (a random payload), and
        submenu
        """

# The content menu itself - menu items are registered as adapters to this
# interface (this is signalled by marking the interface itself with the
# IInterface IMenuItemType)

class IContentMenuItem(interface.Interface):
    """Special menu item type for Plone's content menu."""

directlyProvides(IContentMenuItem, IMenuItemType)

# The sub-menus - because they require additional logic, each of these will be
# implemented with a separate class. We provide markers here to distinguish
# them, although IBrowserMenu is the primary interface through which they are
# looked up. We also provide markers for the special menu items - see
# configure.zcml for more details.

# We use the 'extra' field in the menu items for various bits of information
# the view needs to render the menu. 'extra' will be a dict, with the following
# keys, all optional:
#
#   id           :   The id of the menu item, e.g. the id of the type to add or
#                        the workflow transition
#   state        :   The current state of the item
#   stateTitle   :   The title of the state - to be displayed after the main
#                        item title
#   class        :   A CSS class to apply
#   separator    :   True if the item should be preceded by a separator
#   hideChildren :   True if the item's children should not be rendered

class ITextDirection(interface.Interface):
    """Interface class for utility that returns the text direction on the page"""

class IBodyCSS(interface.Interface):
    """Interface class for utility that return css classes for page body"""

