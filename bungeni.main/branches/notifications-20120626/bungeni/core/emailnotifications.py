import simplejson
from email.mime.text import MIMEText
from threading import Thread
from zope import component
from zope.app.component.hooks import getSite
import smtplib
from bungeni.alchemist import Session
from bungeni.core.interfaces import IMessageQueueConfig
from bungeni.core.notifications import get_mq_connection
from bungeni.models import domain
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
    hostname = settings.hostname
    port = settings.port
    username = settings.username or None
    password = settings.password or None
    connection = smtplib.SMTP(hostname, port)
    connection.set_debuglevel(1)
    if settings.use_tls:
        connection.ehlo()
        connection.starttls()
        connection.ehlo()
        # authenticate if needed
    if username is not None and password is not None:
        connection.login(username, password)
    connection.sendmail(settings.default_sender, msg["To"], msg.as_string())
    connection.quit()
    channel.basic_ack(delivery_tag=method.delivery_tag)


def email_worker():
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(email_notifications_callback,
                          queue="bungeni_email_queue")
    channel.start_consuming()


def email_notifications():
    mq_utility = component.getUtility(IMessageQueueConfig)
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.queue_declare(queue="bungeni_email_queue", durable=True)
    channel.queue_bind(queue="bungeni_email_queue",
                       exchange=str(mq_utility.get_message_exchange()),
                       routing_key="")
    for i in range(mq_utility.get_number_of_workers()):
        task_thread = Thread(target=email_worker)
        task_thread.daemon = True
        task_thread.start()
