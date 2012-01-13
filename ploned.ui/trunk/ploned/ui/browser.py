import types
import interfaces
from zope import interface
from zope import component
from zope.publisher.browser import BrowserView
from zope.security import checkPermission
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from bungeni.core import language

class PloneView(BrowserView):
    def show_editable_border(self):
        return checkPermission("zope.ManageContent", self.context)
    
    def text_direction(self):
        text_direction = component.queryUtility(interfaces.ITextDirection)
        return text_direction and text_direction.get_text_direction() or "ltr"
        
    def is_rtl(self):   
        return language.is_rtl()
        
    def body_css_class(self):
        css = component.queryUtility(interfaces.IBodyCSS)
        return css and css.get_body_css_class() or ""
        
    def have_viewlets(self, view, name):
        gsm = component.getSiteManager()

        specification = map(interface.providedBy, (self.context, self.request, view))
        manager = gsm.adapters.lookup(specification, IViewletManager, name=name)

        iface = tuple(interface.implementedBy(manager))[0]
        specification.append(iface)

        for name, factory in  gsm.adapters.lookupAll(specification, IViewlet):
            # if the factory's constructor (__new__) is different from
            # the built-in class constructor, try instantiating the
            # viewlet to confirm that it's available
            if isinstance(factory.__new__, types.FunctionType):
                viewlet = factory.__new__(
                    factory, self.context, self.request, view, None)
                if viewlet is None:
                    continue
            return True
        return False

    def __call__(self):
        """Return ``self`` such that templates don't need an explicit
        ``nocall`` pragma."""
        
        return self
