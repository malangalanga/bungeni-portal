from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize 

class SpaceView(BrowserView):
    """
    Default view of a Member Space.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request 
        
    #recurse through top level content types
    #list latest entries for each content type
        
    def have_containers(self):
        return len(self.context.getFolderContents()) > 0
        
    def container_categories(self):
        #check to see if the top level container items have children
        containers = self.context.items()
        container_items = []
        for container in containers:
            if len(container[1].getFolderContents()) > 0:
                container_items.append((container[1].title, container[1].id))
        return container_items 
        
    @memoize
    def container_listings(self):
        containers = self.context.items()  
        results = []
        for container in containers:
            if len(container[1].getFolderContents()) > 0:
                container_items = {} 
                container_items["title"] =   container[1].Title()
                container_items["link"] = container[1].Title()   
                container_items["items"] =  [ dict(url=item.getURL(),
                        title=item.Title,
                        description=item.Description,)
                    for item in 
                        container[1].getFolderContents(batch=True, b_size=15)
                ]
                results.append(container_items)               
        return results
               
        


