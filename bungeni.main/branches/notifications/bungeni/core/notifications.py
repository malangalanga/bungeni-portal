import os
import pika
import simplejson
import datetime
from lxml import etree
from threading import Thread
from sqlalchemy import orm
from zope.interface import implements
from zope.component import getUtility
from zope.publisher.interfaces import NotFound
from zope.component import queryMultiAdapter, provideHandler
from zope import security
from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.app.security.settings import Allow
from bungeni.utils.capi import capi
from bungeni.models import domain
from bungeni.core.interfaces import INotificationsUtility, IMessageQueueConfig
from bungeni.core.workflow.interfaces import IWorkflowTransitionEvent
from bungeni.core.serialize import obj2dict
from bungeni.alchemist import Session
from bungeni.alchemist.container import contained
from bungeni.models.utils import get_current_parliament


def get_mq_parameters():
    mq_utility = getUtility(IMessageQueueConfig)
    credentials = pika.PlainCredentials(str(mq_utility.get_username()),
        str(mq_utility.get_password()))
    connection_parameters = pika.ConnectionParameters(
        host=str(mq_utility.get_host()),
        port=mq_utility.get_port(),
        virtual_host=str(mq_utility.get_virtual_host()),
        credentials=credentials,
        channel_max=mq_utility.get_channel_max(),
        frame_max=mq_utility.get_frame_max(),
        heartbeat=mq_utility.get_heartbeat()
    )
    return connection_parameters


def queue_transition_based_notification(document, event):
    mq_utility = getUtility(IMessageQueueConfig)
    domain_class = document.__class__
    unproxied = removeSecurityProxy(document)
    mapper = orm.object_mapper(unproxied)
    primary_key = mapper.primary_key_from_instance(unproxied)
    notifications_utility = getUtility(INotificationsUtility)
    message = {
        "document_id": primary_key,
        "document_type": notifications_utility.get_type(domain_class),
        "source": event.source,
        "destination": event.destination
        }
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    channel.basic_publish(exchange=str(mq_utility.get_exchange()),
                          routing_key=str(mq_utility.get_task_queue()),
                          body=simplejson.dumps(message),
                          properties=pika.BasicProperties(
            content_type="text/plain",
            delivery_mode=1))


def worker():
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()

    def callback(channel, method, properties, body):
        notifications_utility = getUtility(INotificationsUtility)
        message = simplejson.loads(body)
        domain_class = notifications_utility.get_domain(
            message["document_type"])
        roles = notifications_utility.get_transition_based_roles(
            domain_class, message["destination"]
            )
        session = Session()
        document = session.query(domain_class).get(message["document_id"])
        principal_ids = set()
        if document:
            prm = IPrincipalRoleMap(contained(
                    document, get_current_parliament()))
            for role in roles:
                principals = prm.getPrincipalsForRole(role)
                for principal in principals:
                    principal_ids.add(principal[0])
        else:
            pass
        exchange = str(mq_utility.get_exchange())
        for principal_id in principal_ids:
            # create message and add send to exchange
            # TODO: create obj2dict that checks principals permissions to
            # access attributes
            mes = obj2dict(document, 0)
            dthandler = lambda obj: obj.isoformat() if isinstance(obj,
                                                    datetime.datetime) else obj
            channel.basic_publish(exchange=exchange,
                                  routing_key=principal_id,
                                  body=simplejson.dumps(mes, default=dthandler),
                                  properties=pika.BasicProperties(
                    content_type="text/plain",
                    delivery_mode=1))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    mq_utility = getUtility(IMessageQueueConfig)
    channel.basic_consume(callback, queue=str(mq_utility.get_task_queue()))
    channel.start_consuming()


def setup_task_workers():
    mq_utility = getUtility(IMessageQueueConfig)
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    channel.queue_declare(queue=str(mq_utility.get_task_queue()), durable=True)
    channel.queue_bind(queue=str(mq_utility.get_task_queue()),
                       exchange=str(mq_utility.get_exchange()),
                       routing_key=str(mq_utility.get_task_queue()))
    for i in range(mq_utility.get_number_of_workers()):
        task_thread = Thread(target=worker)
        task_thread.daemon = True
        task_thread.start()


def setup_exchange():
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    mq_utility = getUtility(IMessageQueueConfig)
    channel.exchange_declare(exchange=str(mq_utility.get_exchange()),
                             type="direct", durable=True)


class NotificationsUtility(object):
    implements(INotificationsUtility)
    time_based = {}
    transition_based = {}
    domain_type = {}

    def set_transition_based_notification(self, domain_class, state, roles):
        if domain_class not in self.transition_based:
            self.transition_based[domain_class] = {}
        if state not in self.transition_based[domain_class]:
            self.transition_based[domain_class][state] = []
        self.transition_based[domain_class][state].extend(roles)

    def get_transition_based_roles(self, domain_class, state):
        if domain_class in self.transition_based:
            if state in self.transition_based[domain_class]:
                return self.transition_based[domain_class][state]
        return []

    def set_time_based_notification(self, domain_class, state, roles, time):
        if domain_class not in transition_based:
            time_based[domain_class] = {}
        if state not in transition_based[domain_class]:
            time_based[domain_class][state] = []
        if time not in time_based[domain_class][state]:
            time_based[domain_class][state][time] = []
        time_based[domain_class][state][time].extend(roles)

    #!+NOTIFICATIONS(miano, feb 2012) Similar bungeni.core.workspace.WorkspaceUtility
    # TODO - make more generic
    def register_item_type(self, domain_class, item_type):
        """ Stores domain_class -> item_type and vice versa in a dictionary eg.
        domain.Bill -> bill.
        """
        if item_type in self.domain_type.keys():
            raise ValueError("Multiple notification declarations"
                             "with same name - %s") % (item_type)
        if domain_class in self.domain_type.keys():
            raise ValueError("Multiple notification domain classes"
                             "with same name - %s") % (domain_class)
        self.domain_type[item_type] = domain_class
        self.domain_type[domain_class] = item_type

    def get_domain(self, key):
        """Passed a type string returns the domain class"""
        if key in self.domain_type:
            return self.domain_type[key]
        return None

    def get_type(self, key):
        """Passed a domain class returns a string"""
        if key in self.domain_type:
            return self.domain_type[key]
        return None


def load_notification_config(file_name, domain_class):
    """Loads the notification configuration for each documemnt"""
    notifications_utility = getUtility(INotificationsUtility)
    path = capi.get_path_for("notifications")
    file_path = os.path.join(path, file_name)
    item_type = file_name.split(".")[0]
    notifications_utility.register_item_type(domain_class, item_type)
    notification_xml = etree.fromstring(open(file_path).read())
    for notify in notification_xml.iterchildren("notify"):
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
        adapts=(domain_class, IWorkflowTransitionEvent))


def load_notifications(application, event):
    setup_exchange()
    setup_task_workers()
    load_notification_config("bill.xml", domain.Bill)
    load_notification_config("tableddocument.xml", domain.TabledDocument)
    load_notification_config("agendaitem.xml", domain.AgendaItem)
    load_notification_config("motion.xml", domain.Motion)
    load_notification_config("question.xml", domain.Question)
