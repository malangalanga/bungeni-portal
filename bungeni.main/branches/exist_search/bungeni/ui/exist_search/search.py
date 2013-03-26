# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni search implementation
- Searches eXist database from within
"""
log = __import__("logging").getLogger("bungeni.ui.search")

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
from bungeni.ui.widgets import MultiCheckBoxWidget
import interfaces
from bungeni.ui.utils.common import get_context_roles, get_workspace_roles
from bungeni.ui.i18n import _

from bungeni.models import domain, interfaces as model_ifaces

from bungeni.utils import register, naming
from bungeni.capi import capi

def make_url(type_id, type_name, status):
    if type_id and type_name and status:
        domain_class = getattr(domain, type_name, None)
        if domain_class is None:
            domain_class = getattr(domain, naming.model_name(type_name))
        if model_ifaces.IFeatureWorkspace.implementedBy(domain_class):
            ws_roles = get_workspace_roles()
            tabs_config = zope.component.getUtility(IWorkspaceTabsUtility)
            ti = capi.get_type_info(domain_class)
            tab = tabs_config.get_tab(ws_roles[0], domain_class, status)
            if tab:
                return "./my-documents/%s/%s-%s" %(
                    tab, ti.workflow_key, type_id
                )
    return "javascript:void()"

SEARCH_URL = "http://localhost:8088/exist/restxq/ontology"

BASE_MAPPING = {
    "status": "status",
    "type": "docType"
}
MAPPING = {
    "document": {
        "title": "title",
        "author": ["owner", "person", "showAs"],
        "status_date": "statusDate",
    },
    "group": {
        "title": "fullName"
    }
}

def get_node_value(context, key):
    if isinstance(key, list):
        val = None
        ctx = context
        for k in key:
            val = ctx.get(k)
            ctx = val
        return val
    node = context.get(key, None)
    if node:
        if node.has_key("#text"):
            return node.get("#text")
        elif node.has_key("showAs"):
            return node.get("showAs")
        elif node.has_key("value"):
            return node.get("value").get("#text")

def get_results_meta(items_list):
    """return a dict of fields for display
    """
    items = []
    for result in items_list:
        result_type = result.get("for")
        record = result.get(result_type)
        item = {}
        #unique ids take this form Legislature.9-Chamber.2-AgendaItem.54
        unique_id = record.get("unique-id")
        doc_type, obj_key = unique_id.split("-")[-1].split(".")
        status_key = record.get("status").get("value").get("#text")
        item["type"] = doc_type
        item["url"] = make_url(obj_key, doc_type, status_key)
        MAP = BASE_MAPPING.items() + MAPPING.get(result_type, []).items()
        for (key, node_key) in MAP:
            item[key] = get_node_value(record, node_key)
            
        items.append(item) 
    return items

def execute_search(data, prefix):
    data = dict([(key.lstrip("%s." % prefix), 
        (",".join(value) if isinstance(value, list) else value))
        for key,value in data.iteritems() if value])
    search_request = urllib2.Request(SEARCH_URL, urllib.urlencode(data))
    exist_results = json.loads(urllib2.urlopen(search_request).read())
    item_count = int(exist_results.get("total"))
    results = {
        "total": item_count,
        "items": []
    }
    if item_count:
        results["items"] = get_results_meta(
            exist_results.get("ontology"))
    return results

@register.view(ISection, ui_ifaces.IBungeniSkin, 
    name="search.exist", protect={ "zope.Public": register.VIEW_DEFAULT_ATTRS })
class Search(form.PageForm, browser.BungeniBrowserView):
    zope.interface.implements(interfaces.ISearchResults)
    action_method="get"
    template = namedtemplate.NamedTemplate("alchemist.form")
    form_fields = form.FormFields(interfaces.ISearchRequest)
    form_fields["type"].custom_widget = MultiCheckBoxWidget
    form_fields["group"].custom_widget = MultiCheckBoxWidget
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
