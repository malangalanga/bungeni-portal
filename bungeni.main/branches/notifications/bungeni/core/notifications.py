import os
import pika
import simplejson
from lxml import etree
from zope.interface import implements
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from zope.component import queryMultiAdapter, provideHandler, provideSubscriptionAdapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from bungeni.utils.capi import capi
from bungeni.models import domain
from bungeni.core.interfaces import INotificationsUtility, IMessageQueueConfig
from bungeni.core.workflow.interfaces import IWorkflowTransitionEvent


def queue_transition_based_notification(document, event):
    mq_utility = getUtility(IMessageQueueConfig)
    credentials = pika.PlainCredentials(str(mq_utility.get_username()), 
        str(mq_utility.get_password()))
    connection_parameters = pika.ConnectionParameters(
        host = str(mq_utility.get_host()),
        port = mq_utility.get_port(),
        virtual_host = str(mq_utility.get_virtual_host()),
        credentials = credentials,
        channel_max = mq_utility.get_channel_max(),
        frame_max = mq_utility.get_frame_max(),
        heartbeat = mq_utility.get_heartbeat(),
    )
    connection = pika.BlockingConnection(parameters=connection_parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=str(mq_utility.get_exchange()), type="direct", durable=True)
    # Send a message
    channel.basic_publish(exchange=str(mq_utility.get_exchange()),
                      routing_key="test",
                      body="xxx",
                      properties=pika.BasicProperties(content_type="text/plain",
                                                 delivery_mode=1))          
                                                                     
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
    # Register subscriber for domain class
    provideHandler(queue_transition_based_notification,
        adapts=(domain_class, IObjectModifiedEvent))


def load_notifications(application, event):
    load_notification_config("bill.xml", domain.Bill)
    load_notification_config("tableddocument.xml", domain.TabledDocument)
    load_notification_config("agendaitem.xml", domain.AgendaItem)
    load_notification_config("motion.xml", domain.Motion)
    load_notification_config("question.xml", domain.Question)
