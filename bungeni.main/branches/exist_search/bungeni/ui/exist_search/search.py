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
import zope.component
from zope.formlib import form, namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from ploned.ui.interfaces import IBelowContentManager
from bungeni.core.interfaces import ISection, IWorkspaceTabsUtility
from bungeni.ui import interfaces as ui_ifaces, browser
import interfaces
from bungeni.ui.utils.common import get_context_roles, get_workspace_roles
from bungeni.ui.i18n import _

from bungeni.models import domain

from bungeni.utils import register
from bungeni.capi import capi

def make_url(type_id, type_name, status):
    if type_id and type_name and status:
        tabs_config = zope.component.getUtility(IWorkspaceTabsUtility)
        ws_roles = get_workspace_roles()
        domain_class = getattr(domain, type_name)
        ti = capi.get_type_info(domain_class)
        tab = tabs_config.get_tab(ws_roles[0], domain_class, status)
        if tab:
            return "./my-documents/%s/%s-%s" %(
                tab, ti.workflow_key, type_id
            )
    return "#"

SEARCH_URL = "http://localhost:8088/exist/restxq/ontology"
def execute_search(data, prefix):
    data = dict([(key.lstrip("%s." % prefix), value) 
        for key,value in data.iteritems()])
    search_request = urllib2.Request(SEARCH_URL, urllib.urlencode(data))
    exist_results = json.loads(urllib2.urlopen(search_request).read())
    results = {
        "total": exist_results.get("total"),
        "items": []
    }
    for doc in exist_results.get("doc", []):
        record = doc.get("ontology")
        doc = record.get("document") or record.get("group") or record.get("sitting") or {}
        item = {}
        item["type"] = doc.get("docType").get("value").get("#text")
        item["title"] = doc.get("title", {}).get("#text", item["type"])
        item["author"] = doc.get("author", "Unknown Author")
        item["status"] = doc.get("status").get("value").get("#text")
        item["status_date"] = doc.get("statusDate", {}).get("#text", "")
        item["keys"] = doc.keys()
        item["id"] = doc.get("id")
        item["doc_id"] = doc.get("docId", {}).get("#text", "")
        item["url"] = make_url(item["doc_id"], item["type"], item["status"])
        results["items"].append(item)
    return results

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
        self.search_results = execute_search(data, self.prefix)
        self.status = _("Searched for '${search_string}' and found ${count} "
            "items", 
            mapping={ 
                "search_string" : data.get("search") or _("everything"), 
                "count": self.search_results.get("total")
            }
        )

    def validate(self, action, data):
        return form.getWidgetsData(self.widgets, self.prefix, data)

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
    for_display = available
