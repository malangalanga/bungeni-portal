# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni search implementation
- Searches eXist database from within
"""
import json
import urllib2
import urllib
import zope.interface
from zope.formlib import form, namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from ploned.ui.interfaces import IBelowContentManager
from bungeni.core.interfaces import ISection
from bungeni.ui import interfaces as ui_ifaces, browser
import interfaces
from bungeni.ui.utils.common import get_context_roles
from bungeni.ui.i18n import _
from bungeni.utils import register

SEARCH_URL = "http://localhost:8088/exist/restxq/ontology"
def execute_search(data):
    search_request = urllib2.Request(SEARCH_URL, urllib.urlencode(data))
    return json.loads(urllib2.urlopen(search_request).read())

@register.view(ISection, ui_ifaces.IBungeniSkin, 
    name="search.exist", protect={ "zope.Public": register.VIEW_DEFAULT_ATTRS })
class Search(form.PageForm, browser.BungeniBrowserView):
    zope.interface.implements(interfaces.ISearchResults)
    action_method="get"
    template = namedtemplate.NamedTemplate("alchemist.form")
    form_fields = form.FormFields(interfaces.ISearchRequest)
    form_name = _(u"Bungeni Search")
    form_description = _(u"Search Documents in Bungeni")
    show_results = False
    prefix = ""

    def __init__(self, context, request):
        zope.interface.declarations.alsoProvides(
            context, interfaces.ISearchResults
        )
        super(Search, self).__init__(context, request)

    @form.action(_(u"Search"), name="execute-search")
    def handle_search(self, action, data):
        self.show_results = True
        #data["role"] = get_context_roles(self.context, 
        #    self.request.principal)
        self.search_results = execute_search(data)
        self.status = _("Searched for ${search_string} and found ${count} "
            "items", 
            mapping={ 
                "search_string" : data.get("search", _("everything")), 
                "count": self.search_results.get("total")
            }
        )

@register.viewlet(interfaces.ISearchResults, layer=ui_ifaces.IBungeniSkin,
    manager=IBelowContentManager, name="bungeni.exist-search",
    protect=register.PROTECT_VIEWLET_PUBLIC)
class SearchResults(browser.BungeniViewlet):
    """Report preview."""
    
    render = ViewPageTemplateFile("results.pt")
    
    def update(self):
        if self.available:
            self.search_results = self._parent.search_results

    @property
    def available(self):
        return self._parent.show_results
