from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bungenicms.repository import repositoryMessageFactory as _
from Products.CMFCore.utils import getToolByName
from bungenicms.repository.browser.utils import slugify, country_vocabulary

log = __import__("logging").getLogger("bungenicms.repository.browser")

# * globals * 
BROWSE_VIEW = "browse-items"
BROWSE_INDICES = {u'subject_terms': _("Subject Terms"),
                  u'item_authors': _("Author"),
                  u'Title': _("Title"),
                  u'issue_date': _("Issue date"),
                  u'legislative_type': _("Legislative Type"),
		  u'item_publisher': _("Published By"),
}
FILTER_KEY = u"index"
SEARCH_KEY = u"term"
SEARCH_TEXT = u"search_query"
DEFAULT_SORT_INDEX = u'path' 
DEFAULT_SORT_ORDER = u'ascending'
DEFAULT_META_TYPES = ['RepositoryItem',
                      'RepositoryCollection',
                      'RepositoryCommunity']

#also need to determine render methods for various keys

class RepositoryItemsBrowser(BrowserView):
    """
    Repository Items Browser
    """
    def hasSearchTerm(self):
        return self.request.form.has_key(SEARCH_KEY)
    
    def hasFilter(self):
        return self.request.form.has_key(FILTER_KEY)
        
    def getFilterKey(self):
        return self.request.form.get(FILTER_KEY, '') 

    def getSearchTerms(self):
        return self.request.form.get(SEARCH_KEY, '')

    def getIndexItems(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        #import pdb;pdb.set_trace()
        filter_index = self.getFilterKey()
        if filter_index in catalog.indexes():
            try:
                return catalog.uniqueValuesFor(filter_index)
            except NotImplementedError:
                #TODO use separate listing
                return None
        else:
            return None
            
    def getFilterTitle(self):
        filter_title = BROWSE_INDICES[self.getFilterKey()]
        title_message = _(u'bungenicms_repository_filter_title_message',
                         default = u"Browsing results by ${filter_title}",
                         mapping = {u'filter_title': filter_title})
        return title_message

    def getCatalogItems(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query_path = '/'.join(self.context.getPhysicalPath())
        query = dict(path = dict(query = query_path),
                     review_state = 'published')
        index_filter = self.getFilterKey()
        if index_filter:
            query[index_filter] = self.getSearchTerms()
        return catalog(query)


class SearchItems(BrowserView):
    """
    Search interfaces for repository containers
    """
        
    def hasFilter(self):
        return self.request.form.has_key(SEARCH_TEXT)

    def getSearchText(self):
        return self.request.form.get(SEARCH_TEXT, '')

    def getSearchMessage(self, count):
        search_message = _(u'bungenicms_repository_search_results_message',
                            default = u"Found ${item_count} items\
                            matching \"${search_query}\"",
                            mapping = {
                                u'item_count': count,
                                u'search_query': self.getSearchText()
                            })
        return search_message

    def executeSearch(self):
        search_path = '/'.join(self.context.getPhysicalPath())
        catalog = getToolByName(self.context, u'portal_catalog')
        query = dict(
                    SearchableText = self.getSearchText(),
                    path = dict(query = search_path),
                    review_state = u'published',
                    sort_on = DEFAULT_SORT_INDEX,
                    sort_order = DEFAULT_SORT_ORDER,
                    meta_type = DEFAULT_META_TYPES
        )
        return catalog(query)

    def getSearchResults(self):
        search_results = self.executeSearch()
        search_message = self.getSearchMessage(len(search_results))
        return dict(search_results = search_results,
                    search_message = search_message)


class CommunityRedirect(BrowserView):
    """
    Redirects users to target community based on metadata
    """
    @property
    def mtool(self):
        return getToolByName(self.context, 'portal_membership')
        
    @property
    def context_object(self):
        return aq_inner(self.context)

    def __call__(self):
        return self.request.response.redirect(self.getCommunityAddress())


    def getCommunityAddress(self):
        if not self.mtool.isAnonymousUser():
            user = self.mtool.getAuthenticatedMember()
            country = user.getProperty("country", None)
            if country is not None:
                country_id = ''
                try:
                    term = country_vocabulary.getTerm(country)
                    country_id = slugify(term.title)
                except LookupError:
                    log.error
                if country_id in self.context.objectIds():
                    community = getattr(self.context_object, country_id)
                    return community.absolute_url()
        return self.context_object.absolute_url()
        
