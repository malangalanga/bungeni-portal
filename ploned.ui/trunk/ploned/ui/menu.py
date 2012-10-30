"""
$Id$

replacement of the default menu implementation for our global tabs, since
we ran into issues on traversability checks done when we're doing site relative
addressing in these tabs.

---
Kapil Thangavelu 

"""
log = __import__("logging").getLogger("ploned.ui.menu")

import sys
import zope.component

from zope.security.proxy import removeSecurityProxy
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized

from zope.interface import providedBy, Interface
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.browsermenu.menu import BrowserMenu, getMenu
from zope.browsermenu.interfaces import IBrowserMenu
from zope.app.component.hooks import getSite

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.pagetemplate.engine import Engine
#from bungeni.ui import z3evoque

from bungeni.ui.utils import url, debug
#from ploned.ui.interfaces import IViewView

def pos_action_in_url(action, request_url):
    """Get index of action in URL, or None."""
    # strip all leading combinations of "." "/" or "@" characters
    normalized_action = action.lstrip("./@")
    return request_url.rfind(normalized_action)

# !+ID-GENERATION(ah, 17-05-2011) - added back this api which was removed in 
# r8256. All the address add action menus were getting the ids as container 
# paths e.g. ./addresses/add since it was falling back to using the action 
# name for id generation
def action_to_id(action):
    return action.strip("/").replace("/", "-").replace(".", "").strip("-")


def make_absolute(action, local_url, site_url):
    if action.startswith("http://") or action.startswith("https://"):
        return action
    if action.startswith("."):
        return "%s/%s" % (local_url, action[1:].lstrip("/"))
    if action.startswith("/"):
        return "%s/%s" % (site_url, action[1:])
    return "%s/%s" % (local_url, action)

def check_availability(menu_item):
    """check availability of a menu against its permission and filter"""
    available = True
    if menu_item.permission is not None:
        available = checkPermission(menu_item.permission, menu_item.context)
    if menu_item.filter is not None:
        try:
            available = menu_item.filter(Engine.getContext(
                context = menu_item.context,
                nothing = None,
                request = menu_item.request,
                modules = sys.modules,
                ))
        except Unauthorized:
            available = False
    return available
        

class PloneBrowserMenu(BrowserMenu):
    """This menu class implements the ``getMenuItems`` to conform with
    Plone templates.
    """
    
    def getMenuItems(self, obj, request):
        obj = removeSecurityProxy(obj)
        menu = tuple(zope.component.getAdapters(
            (obj, request), self.getMenuItemType()))
        # filter out all items which you do not have the permissions for
        result = [ item for name, item in menu if
            check_availability(item) ]
        # Now order the result. This is not as easy as it seems.
        # (1) Look at the interfaces and put the more specific menu entries
        #     to the front. 
        # (2) Sort unambigious entries by order and then by title.
        ifaces = list(providedBy(removeSecurityProxy(obj)).__iro__)
        max_key = len(ifaces)
        def iface_index(item):
            iface = item._for
            if not iface:
                iface = Interface
            if zope.interface.interfaces.IInterface.providedBy(iface):
                return ifaces.index(iface)
            if isinstance(removeSecurityProxy(obj), item._for):
                # directly specified for class, this goes first.
                return -1
            # no idea. This goes last.
            return max_key
        result = [(item.order, iface_index(item), item.title, item)
                  for item in result]
        result.sort()
        # !+ replace above with super getMenuItems()
        local_url = url.absoluteURL(obj, request)
        site_url = url.absoluteURL(getSite(), request)
        request_url = request.getURL()
        
        items = []
        selected_index = None
        current_pos = -1
        
        for index, (order, iface_index, title, item) in enumerate(result):
            # !+ for some reason, for the generic container listing views, the 
            # context_actions menu comes out with a single item pointing to 
            # "@@index" i.e. itself... we ignore it:
            if item.action=="@@index":
                continue
            
            extra = item.extra or {}
            # if no id has been explictly set, get one in some way or another...
            # !+ID-GENERATION(ah, 17-05-2011) - added call to action_to_id 
            # around item.action as other-wise it returns an invalid @id 
            # attribute (see comment above)
            extra.setdefault("id",
                # try "id", BrowserMenu, bungeni.ui.menu.BrowserSubMenuItem
                # (that picks an id value off item.submenuId) otherwise use
                # the "action" value, zope.browsermenu.BrowserMenuItem
                getattr(item, "id", None) or action_to_id(item.action)
            )
            # !+CSS_ID(mr, may-2011) the CSS menu styling should NOT be based 
            # on element id, it is unnecessarily brittle and limited e.g. what
            # happens if you wish to render a menu twice, on top and bottom of
            # a page? Styling selectors should be connected only via classes
            # (not even element tag names). The use of an element id should be 
            # limited to only known-to-be-unique contrainers in the page e.g.
            # "content", "top-menu-bar", "footer", etc. 
            
            if IBrowserSubMenuItem.providedBy(item):
                submenu = getMenu(item.submenuId, obj, request)
            else:
                submenu = None
                extra["hideChildren"] = True
            
            _url = make_absolute(item.action, local_url, site_url)
            
            if submenu:
                for menu in submenu:
                    menu["url"] = make_absolute(
                        menu["action"], local_url, site_url)
            
            pos = pos_action_in_url(item.action, request_url)
            if pos and pos > current_pos:
                # !+ should really only reset this only once, 
                # and pos *should* always be len(base_url)
                current_pos = pos
                selected_index = index
            
            items.append({
                "title": title,
                "description": item.description,
                "action": item.action,
                "url": _url,
                "selected": u"",
                # !+MENU_ICON(mr, aug-2010) remove, icon always managed via CSS
                "icon": item.icon,
                "extra": extra,
                "submenu": submenu})
        
        if selected_index is not None:
            items[selected_index]["selected"] = u"selected"
        return items

class ContentMenuProvider(object):
    """Content menu."""
    
    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request
    
    def update(self):
        pass
    
    # evoque
    #render = z3evoque.ViewTemplateFile("ploned.html#action_menus")
    # zpt
    render = ViewPageTemplateFile("templates/contentmenu.pt")
    
    def available(self):
        #if menu is empty, hide
        if not self.menu():
            return False
        return True
    
    def menu(self):
        menu = zope.component.getUtility(IBrowserMenu, name="plone_contentmenu")
        items = menu.getMenuItems(self.context, self.request)
        items.reverse()
        return items

