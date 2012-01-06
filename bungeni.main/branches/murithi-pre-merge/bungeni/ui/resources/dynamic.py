import json
import zope.interface
import zope.publisher.interfaces.browser
from bungeni.utils.capi import capi
from bungeni.ui.i18n import _
from bungeni.core.translation import (translate_i18n as i18n, 
    get_request_language
)

RESOURCE_MAPPING = {
    "scheduler-globals.js": "scheduler_globals"
}

## some global strings to i18n ##
YES = _(u"Yes")
NO = _(u"No")
OKAY = _(u"Okay")
NOTICE = _(u"Notice")
WORKING = _(u"Working")

def get_globals(group_name, **kwargs):
    language = kwargs.get("language", "en")
    globals_map = {
        "SCHEDULER_GLOBALS" : {
            "types": {
                "HEADING": "heading",
                "TEXT": "text"
            },
            "json_listing_url" : "./items/jsonlisting?sort=sort_planned_order&dir=asc",
            "save_schedule_url": "./items/save-schedule",
            "schedulable_items_json_url" : "./schedulable-items-json",
            "column_title": i18n(_(u"Title"), language),
            "column_type": i18n(_(u"Type"), language),
            "column_mover": i18n(_(u"Moved by"), language),
            "column_status": i18n(_(u"Status"), language),
            "column_status_date": i18n(_(u"Date"), language),
            "column_registry_number": i18n(_(u"No."), language),
            "column_mover": i18n(_(u"Mover"), language),
            "text_button_text": i18n(_(u"add text"), language),
            "heading_button_text": i18n(_(u"add heading"), language),
            "remove_button_text": i18n(_(u"remove selected items"), language),
            "save_button_text": i18n(_(u"save changes"), language),
            "discard_button_text": i18n(_(u"discard changes"), language),
            "current_schedule_title": i18n(_(u"Agenda"), language),
            "available_items_title": i18n(_(u"Available Items"), language),
            "initial_editor_text": i18n(
                _(u"change this text"), language
            ),
            "delete_dialog_header": i18n(_(u"Remove item from schedule")),
            "delete_dialog_text": i18n(
                _(u"Are you sure you want to remove this item from schedule ?"),
                language
            ),
            "delete_dialog_confirm": i18n(YES, language),
            "delete_dialog_cancel": i18n(NO, language),
            "save_dialog_header": i18n(NOTICE, language),
            "save_dialog_empty_message": i18n(
                _(u"No items have been scheduled. Add something then save."), 
                language
            ),
            "save_dialog_confirm": i18n(OKAY, language),
            "saving_dialog_header": i18n(WORKING, language),
            "saving_dialog_text": i18n(_(u"saving changes to schedule..."), 
                language
            ),
            "saving_dialog_refreshing": i18n(
                _(u"reloading schedule data"), language
            ),
            "saving_dialog_exception": i18n(
                _(u"there was an error while saving the schedule"), language
            ),
            "schedulable_types": ["bill", "question", "motion", 
                "tableddocument", "agendaitem", "heading"
            ]
        }
    }
    return globals_map.get(group_name, {})

class DynamicDirectoryFactory:
    """Allows generation of static resources whose content is contextual.
    
    For example, we want some system parameters to be available to certain
    registered JavaScript resources
    """
    
    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher
    )

    def __init__(self, source, checker, name):
        self.name = name
        self.__Security_checker__ = checker
        self.request_language = capi.default_language
    
    def __call__(self, name):
        return self
    
    def __getitem__(self, name):
        return lambda:"/@@/%s/%s" % (self.name, name)
    
    def publishTraverse(self, request, name):
        self.request_language = get_request_language()
        return getattr(self, RESOURCE_MAPPING.get(name))
    
    def scheduler_globals(self):
        return """var scheduler_globals = %s;""" % json.dumps(
            get_globals("SCHEDULER_GLOBALS", language=self.request_language)
        )

