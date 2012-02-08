import os
from lxml import etree
from zope.interface import implements
from bungeni.core.interfaces import INotificationsUtility
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from zope.component import queryMultiAdapter
from bungeni.utils.capi import capi
from bungeni.core.interfaces import INotificationsUtility
from bungeni.models import domain

class NotificationsUtility(object):
    implements(INotificationsUtility)
    time_based = {}
    transition_based = {}
    
    def set_transition_based_notification(domain_class, state, roles):
        if domain_class not in transition_based:
            transition_based[domain_class] = {}
        if state not in transition_based[domain_class]:
            transition_based[domain_class][state] = []
        transition_based[domain_class][state].extend(roles)
        
    def set_time_based_notification(domain_class, state, roles, time):
        if domain_class not in transition_based:
            time_based[domain_class] = {}
        if state not in transition_based[domain_class]:
            time_based[domain_class][state] = []
        if time not in time_based[domain_class][state]:
            time_based[domain_class][state][time] = []
        time_based[domain_class][state][time].extend(roles)
        
def load_notification_config(file_name, domain_class):
    """Loads the notification configuration for each documemnt"""
    notifications_utility = getUtility(INotificationsUtility)
    path = capi.get_path_for("notifications")
    file_path = os.path.join(path, file_name)
    item_type = file_name.split(".")[0]
    notification_xml = etree.fromstring(open(file_path).read())
    for notify in notification_xml.iterchildren("notifications"):
        roles = notify.get("roles").split()
        if notify.get("onstate"):
            states = notify.get("onstate").split()
            for state in states:
                notifications_utility.set_transition_based_notification(
                        domain_class, state, roles)
        elif notification.get("afterstate"):
            states = notify.get("afterstate").split()
            time = notify.get("time")
            for state in states:
                notifications_utility.set_time_based_notification(
                        domain_class, state, roles, time)
        else:
            raise ValueError("Please specify either onstate or afterstate")


def load_notifications(application, event):
    load_notification_config("bill.xml", domain.Bill)
    load_notification_config("tableddocument.xml", domain.TabledDocument)
    load_notification_config("agendaitem.xml", domain.AgendaItem)
    load_notification_config("motion.xml", domain.Motion)
    load_notification_config("question.xml", domain.Question)
