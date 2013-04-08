from Products.Five.browser import BrowserView
from bungenicms.repository.interfaces.repositorycollection import \
 IRepositoryCollection
from bungenicms.repository.interfaces.repositoryitem import \
 IRepositoryItem
from bungenicms.repository.interfaces.repositorycommunity import \
 IRepositoryCommunity

class CommunityBase(BrowserView):
	"""
	"""
	def getCollections(self):
		catalog = self.context.portal_catalog
		search_path = '/'.join(self.context.getPhysicalPath())
		search_query = {
			'path' : dict(query=search_path),
			'object_provides' : IRepositoryCollection.__identifier__,
			'sort_on' : 'sortable_title', 
			'sort_order' : 'ascending',
		}
		return catalog.searchResults(search_query)

	def getRecentItems(self):
		catalog = self.context.portal_catalog
		search_path = '/'.join(self.context.getPhysicalPath())
		search_query = {
			'path' : dict(query=search_path),
			'object_provides' : IRepositoryItem.__identifier__,
		}
		return catalog.searchResults(search_query)

	def getSubCommunities(self):
		catalog = self.context.portal_catalog
		search_path = '/'.join(self.context.getPhysicalPath())
		search_query = {
			'path' : dict(query=search_path),
			'object_provides' : IRepositoryCommunity.__identifier__,
			'sort_on' : 'sortable_title', 
			'sort_order' : 'ascending',
		}
		return catalog.searchResults(search_query)
