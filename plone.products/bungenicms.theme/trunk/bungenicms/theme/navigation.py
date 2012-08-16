from zope import interface

from plone.app.layout.viewlets import common
from plone.app.layout.navigation.root import getNavigationRoot

from Acquisition import aq_inner

from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

class PersonalBarViewlet(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('personal_bar.pt')
    subcontext = ()
    
    def update(self):
        super(PersonalBarViewlet, self).update()

        # compute and set 'subcontext' which is the second-level
        # navigation context
        try:
            parents = self.aq_parent.aq_inner.aq_chain
            subcontext = parents[-4]
            if len(parents) > 6:
                selected_url = parents[-5].absolute_url()
            else:
                selected_url = self.context.absolute_url()            
            if IFolderish.providedBy(subcontext):
                self.subcontext = [{
                    'url': item.absolute_url(),
                    'title': item.title_or_id(),
                    'selected':selected_url} \
                    for item in subcontext.objectValues()
                        if not item.exclude_from_nav()]      
        except IndexError:
            pass
        
class CatalogNavigationTabs(BrowserView):
    interface.implements(INavigationTabs)

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = aq_inner(self.context)

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions.get(category, []):
                data = actionInfo.copy()
                data['name'] = data['title']
                result.append(data)

        # check whether we only want actions
        if site_properties.getProperty('disable_folder_sections', False):
            return result

        customQuery = getattr(context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        rootPath = getNavigationRoot(context)
        query['path'] = {'query' : rootPath, 'depth' : 1}

        query['portal_type'] = utils.typesToList(context)

        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty(
                'wf_states_to_show', [])

        query['is_default_page'] = False
        
        if site_properties.getProperty('disable_nonfolderish_sections', False):
            query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(**query)

        # now add the content to results
        for item in rawresult:
            if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : item.getId,
                        'url'        : item_url,
                        'description': item.Description}
                result.append(data)
        return result
        
class PathBarViewlet(common.PathBarViewlet):
    index = ViewPageTemplateFile('path_bar.pt')       
