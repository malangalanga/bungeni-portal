import pika
import simplejson

from zope import component
from bungeni.alchemist import Session
from bungeni.core.interfaces import IMessageQueueConfig
from bungeni.core.notifications import get_mq_parameters
from bungeni.models import domain

def email_notifications_callback(channel, method, properties, body):
    message = simplejson.loads(body)
    principal_ids = message["principal_ids"]
    session = Session()
    users = session.query(domain.User).filter(
        domain.User.login.in_(principal_ids)).all()
    

def email_notifications():
    mq_utility = component.getUtility(IMessageQueueConfig)
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    channel.queue_declare(queue="bungeni_email_queue", durable=True)
    channel.queue_bind(queue="bungeni_email_queue",
                       exchange=str(mq_utility.get_message_exchange()),
                       routing_key="")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(email_notifications_callback, queue="")
    channel.start_consuming()
