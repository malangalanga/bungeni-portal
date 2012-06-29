import pika
import simplejson
from email.mime.text import MIMEText
from threading import Thread
from zope import component
from zope.app.component.hooks import getSite
from bungeni.alchemist import Session
from bungeni.core.interfaces import IMessageQueueConfig
from bungeni.core.notifications import get_mq_parameters
from bungeni.models import domain
from bungeni.server.smtp import dispatch
from bungeni.models.settings import EmailSettings


def email_notifications_callback(channel, method, properties, body):
    message = simplejson.loads(body)
    principal_ids = message["principal_ids"]
    session = Session()
    users = session.query(domain.User).filter(
        domain.User.login.in_(principal_ids)).all()
    recipients = [user.email for user in users]
    settings = EmailSettings(getSite())
    msg = MIMEText("test")
    msg["Subject"] = "Test email"
    msg["From"] = settings.default_sender
    msg["To"] = ', '.join(recipients)
    dispatch(msg)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def email_worker():
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(email_notifications_callback,
                          queue="bungeni_email_queue")
    channel.start_consuming()


def email_notifications():
    mq_utility = component.getUtility(IMessageQueueConfig)
    connection = pika.BlockingConnection(parameters=get_mq_parameters())
    channel = connection.channel()
    channel.queue_declare(queue="bungeni_email_queue", durable=True)
    channel.queue_bind(queue="bungeni_email_queue",
                       exchange=str(mq_utility.get_message_exchange()),
                       routing_key="")
    for i in range(mq_utility.get_number_of_workers()):
        task_thread = Thread(target=email_worker)
        task_thread.daemon = True
        task_thread.start()
