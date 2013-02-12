from zope import component
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

import domain, utils
    
@component.adapter(domain.AgendaItem, IObjectCreatedEvent)
def set_parliament_id(context, event):
    if context.parliament_id is None:
        parliament =  utils.get_parliament_for_group_id(context.group_id)
        context.parliament_id = parliament.group_id
