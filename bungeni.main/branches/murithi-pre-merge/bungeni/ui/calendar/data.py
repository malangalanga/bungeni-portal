# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Data loader module for scheduler

$Id$
"""
import json
from sqlalchemy import orm, sql
from bungeni.models import domain
from bungeni.core.dc import IDCDescriptiveProperties
from bungeni.core.workflow.interfaces import IWorkflow
from bungeni.core.translation import translate_i18n
from bungeni.ui.tagged import get_states
from bungeni.ui.utils import date, common
from bungeni.alchemist import Session
from bungeni.ui.i18n import _

def get_schedulable_types():
    #!+CALENDAR(mb, Jan-2012) This should come from capi or workflow configuration
    return ["bill", "question", "motion", "tableddocument", "agendaitem", "heading"]


def get_filter_config(tag="tobescheduled"):
    return dict(
        [ (item_type, 
            { 
                "label": _(u"choose status"),
                "menu": [ 
                    { 
                        "text": IWorkflow(domain.DOMAIN_CLASSES[item_type]()).get_state(status).title, 
                        "value": status 
                    } 
                    for status in get_states(item_type, tagged=[tag])
                ]
            }
           ) 
            for item_type in get_schedulable_types()
        ]
    )

class SchedulableItemsGetter(object):
    item_type = None
    filter_states = []
    group_filter = False
    domain_class = None
    
    def __init__(self, context, item_type, filter_states=None, 
        group_filter=False, item_filters={}
    ):
        self.context = context
        self.item_type = item_type
        self.filter_states = filter_states or get_states(item_type, 
            tagged=["tobescheduled"]
        )
        self.group_filter = group_filter
        try:
            self.domain_class = domain.DOMAIN_CLASSES[item_type]
        except AttributeError:
            raise AttributeError("Domain Class mapping has no such type %s" %
                item_type
            )
        self.item_filters = item_filters
    
    @property
    def group_id(self):
        parent=self.context
        while parent is not None:
            group_id = getattr(parent, "group_id", None)
            if group_id:
                return group_id
            else:
                parent = parent.__parent__
        raise ValueError("Unable to determine group.")
    
    def query(self):
        items_query = Session().query(self.domain_class).filter(
            self.domain_class.status.in_(self.filter_states)
        )
        if len(self.item_filters):
            for (key, value) in self.item_filters.iteritems():
                column = getattr(self.domain_class, key)
                #!+SCHEDULING(mb, Jan-2011) extend query spec to include sql filters
                if "date" in key:
                    if "|" in value:
                        start, end = value.split("|")
                        expression = sql.between(column, start, end)
                    else:
                        expression = (column==value)
                else:
                    expression = (column==value)
                items_query = items_query.filter(expression)
        if self.group_filter:
            items_query = items_query.filter(
                self.domain_class.group_id==self.group_id
            )
        return tuple(items_query)


    def as_json(self):
        date_formatter = date.getLocaleFormatter(common.get_request(), "date",
            "medium"
        )
        items_json = dict(
            items = [
                dict(
                    item_type = self.item_type,
                    item_id = orm.object_mapper(item).primary_key_from_instance(
                        item
                    )[0],
                    item_title = IDCDescriptiveProperties(item).title,
                    status = IWorkflow(item).get_state(item.status).title,
                    status_date = ( date_formatter.format(item.submission_date) 
                        if hasattr(item, "submission_date") else None
                    ),
                    registry_number = ( item.registry_number if
                        hasattr(item, "registry_number") else None
                    ),
                    mover = ( IDCDescriptiveProperties(item.owner).title if
                        hasattr(item, "owner") else None
                    )
                )
                for item in self.query()
            ]
        )
        return json.dumps(items_json)
