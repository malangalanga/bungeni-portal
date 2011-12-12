# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Data loader module for scheduler

$Id$
"""
import json
from sqlalchemy import orm
from bungeni.models import domain
from bungeni.core.dc import IDCDescriptiveProperties
from bungeni.core.workflow.interfaces import IWorkflow
from bungeni.ui.tagged import get_states
from bungeni.alchemist import Session

class SchedulableItemsGetter(object):
    item_type = None
    filter_states = []
    group_filter = False
    domain_class = None
    
    def __init__(self, context, item_type, filter_states=None, group_filter=False):
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
        if self.group_filter:
            items_query = items_query.filter(
                self.domain_class.group_id==self.group_id
            )
        return tuple(items_query)


    def as_json(self):
        items_json = dict(
            items = [
                dict(
                    item_type = self.item_type,
                    item_id = orm.object_mapper(item).primary_key_from_instance(
                        item
                    )[0],
                    item_title = IDCDescriptiveProperties(item).title,
                    status = IWorkflow(item).get_state(item.status).title
                )
                for item in self.query()
            ]
        )
        return json.dumps(items_json)
