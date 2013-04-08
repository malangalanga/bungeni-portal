from zope.interface import implements
from zope.component import adapts, getMultiAdapter, queryUtility
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from bungenicms.repository import repositoryMessageFactory as _
from bungenicms.repository.interfaces import IRepositoryItemBrowser
from bungenicms.repository.browser.itembrowser import BROWSE_INDICES, \
                                                BROWSE_VIEW,\
                                                FILTER_KEY

from Acquisition import aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IRepositoryNavigatorPortlet(IPortletDataProvider):
    """
    """
    

class Assignment(base.Assignment):
    implements(IRepositoryNavigatorPortlet)
    
    @property
    def title(self):
        return _('Content Browser')
        
class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, 
        data)
        
    @property
    def available(self):
        current_object = aq_inner(self.context)
        show = False
        if current_object:
            return IRepositoryItemBrowser.providedBy(current_object)
        return show

    def menuitems(self):
        menu_items = [
            {'title': value, 
            'view_link': BROWSE_VIEW+'?'+FILTER_KEY+'='+key
            }
            for key,value in BROWSE_INDICES.iteritems()
        ]
        return menu_items

    render = ViewPageTemplateFile("repositorynavigator.pt")

class AddForm(base.AddForm):
    label = _("Add repository navigator portlet")
    description = _("This portlet renders custom navigation for\
     repository content types")
    
    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    label = _("Edit repository navigator portlet")
    description = _("This portlet renders custom navigation for \
    repository content types")
