from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from itembrowser import BROWSE_INDICES

class BrowseItemsMenu(ViewletBase):
    render = ViewPageTemplateFile("templates/browse_items_menu.pt")

    def update(self):
        self.item_filters = self.getDocumentFilters()
    
    def getDocumentFilters(self):
        item_filters= [{'index': index, 'title':title}
                       for index,title in BROWSE_INDICES.items()
                      ]
        return item_filters
        

class SearchControl(ViewletBase):
    render = ViewPageTemplateFile("templates/search_control.pt")
