from Products.Five import BrowserView
from bungenicms.repository.interfaces import IRepositoryCollection

log = __import__("logging").getLogger("bungenicms.workspaces.browser")

class LibraryView(BrowserView):

    def getCollections(self):
        catalog = self.context.portal_catalog
        results = catalog.searchResults(id="groups")
	if len(results) == 1:
            p_path = results[0].getPath()
            search_query = {
                'path' : p_path,
                'object_provides' : IRepositoryCollection.__identifier__,
                'sort_on' : 'sortable_title', 
                'sort_order' : 'ascending',
		}
        return catalog.searchResults(search_query)

