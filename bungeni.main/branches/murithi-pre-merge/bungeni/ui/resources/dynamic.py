import json
import zope.interface
import zope.publisher.interfaces.browser
from bungeni.ui.i18n import _

RESOURCE_MAPPING = {
    "scheduler-globals.js": "scheduler_globals"
}

SCHEDULER_GLOBALS = {
    "json_listing_url" : "./items/jsonlisting",
    "column_title": _(u"Title"),
    "column_type": _(u"Type")
}

class DynamicDirectoryFactory:
    """Allows generation of resources required
    """
    
    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher
    )

    def __init__(self, source, checker, name):
        self.name = name
        self.__Security_checker__ = checker
    
    def __call__(self, name):
        return self
    
    def __getitem__(self, name):
        return lambda:"/@@/%s/%s" % (self.name, name)
    
    def publishTraverse(self, request, name):
        return getattr(self, RESOURCE_MAPPING.get(name))
    
    def scheduler_globals(self):
        return """var scheduler_globals = %s;""" % json.dumps(SCHEDULER_GLOBALS)

