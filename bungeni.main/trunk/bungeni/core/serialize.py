# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

""" Utilities to serialize objects to XML

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.serialize")

import os
import time
from StringIO import StringIO
from zipfile import ZipFile
from threading import Thread
from xml.etree.cElementTree import Element, ElementTree
from tempfile import NamedTemporaryFile as tmp
import simplejson

import zope.component
from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent import IObjectModifiedEvent, IObjectCreatedEvent

from sqlalchemy.orm import class_mapper, object_mapper
from sqlalchemy.types import Binary

from ore.alchemist.container import valueKey
from bungeni.alchemist.container import stringKey
from bungeni.alchemist import Session
from bungeni.core.workflow.states import (get_object_state_rpm, 
    get_head_object_state_rpm
)
from bungeni.core.interfaces import IMessageQueueConfig
from bungeni.core.workflow.interfaces import (IWorkflow, IStateController,
    IWorkflowed, IWorkflowController, InvalidStateError
)
from bungeni.core.notifications import get_mq_connection
from bungeni.models import interfaces, domain
from bungeni.models.utils import obj2dict, get_permissions_dict
from bungeni.utils import register, naming

import pika

def setupStorageDirectory(part_target="xml_db"):
    """ Returns path to store xml files.
    """
    store_dir = __file__
    x = ""
    while x != "src":
        store_dir, x = os.path.split(store_dir)
    store_dir = os.path.join(store_dir, "parts", part_target)
    if os.path.exists(store_dir):
        assert os.path.isdir(store_dir)
    else:
        os.mkdir(store_dir)
    
    return store_dir


def publish_to_xml(context):
    """Generates XML for object and saves it to the file. If object contains
    attachments - XML is saved in zip archive with all attached files. 
    """
    include = []
    # list of files to zip
    files = []
    # data dict to be published
    data = {}
    
    context = removeSecurityProxy(context)
    
    if interfaces.IFeatureVersion.providedBy(context):
        include.append("versions")
    if interfaces.IFeatureAudit.providedBy(context):
        include.append("event")
    
    exclude = ["data", "event", "attachments", "changes"]
    
    # include binary fields and include them in the zip of files for this object
    for column in class_mapper(context.__class__).columns:
        if column.type.__class__ == Binary:
            exclude.append(column.key)
            content = getattr(context, column.key, None)
            if content:
                bfile = tmp(delete=False)
                bfile.write(content)
                files.append(bfile.name)
                data[column.key] = dict(
                    saved_file=os.path.basename(bfile.name)
                )
                bfile.close()
    data.update(
        obj2dict(context, 1, 
            parent=None,
            include=include,
            exclude=exclude
        )
    )
    obj_type = IWorkflow(context).name    
    tags = IStateController(context).get_state().tags
    if tags:
        data["tags"] = tags
    permissions = get_object_state_rpm(context).permissions
    data["permissions"] = get_permissions_dict(permissions)
    data["changes"] = []
    for change in getattr(context, "changes", []):
        change_dict = obj2dict(change, 0, parent=context)
        change_permissions = get_head_object_state_rpm(change).permissions
        change_dict["permissions"] = get_permissions_dict(change_permissions)
        data["changes"].append(change_dict)
    
    # setup path to save serialized data 
    path = os.path.join(setupStorageDirectory(), obj_type)
    if not os.path.exists(path):
        os.makedirs(path)
    
    # xml file path
    file_path = os.path.join(path, stringKey(context)) 
    
    if interfaces.IFeatureAttachment.providedBy(context):
        attachments = getattr(context, "attachments", None)
        if attachments:
            data["attachments"] = []
            for attachment in attachments:
                # serializing attachment
                attachment_dict = obj2dict(attachment, 1,
                    parent=context,
                    exclude=["data", "event", "versions"])
                permissions = get_object_state_rpm(attachment).permissions
                attachment_dict["permissions"] = \
                    get_permissions_dict(permissions)
                # saving attachment to tmp
                attached_file = tmp(delete=False)
                attached_file.write(attachment.data)
                attached_file.close()
                files.append(attached_file.name)
                attachment_dict["saved_file"] = os.path.basename(
                    attached_file.name
                )
                data["attachments"].append(attachment_dict)

    
    # zipping xml, attached files plus any binary fields
    # also remove the temporary files
    if files:
        #generate temporary xml file
        temp_xml = tmp(delete=False)
        temp_xml.write(serialize(data, name=obj_type))
        temp_xml.close()
        #write attachments/binary fields to zip
        zip_file = ZipFile("%s.zip" % (file_path), "w")
        for f in files:
            zip_file.write(f, os.path.basename(f))
            os.remove(f)
        #write the xml
        zip_file.write(temp_xml.name, "%s.xml" % os.path.basename(file_path))
        os.remove(temp_xml.name) 
        zip_file.close()
    else:
        # save serialized xml to file
        with open("%s.xml" % (file_path), "w") as xml_file:
            xml_file.write(serialize(data, name=obj_type))
            xml_file.close()

    #publish to rabbitmq outputs queue
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    publish_file_path = "%s.%s" %(file_path, ("zip" if files else "xml"))
    channel.basic_publish(
        exchange=SERIALIZE_OUTPUT_EXCHANGE,
        routing_key=SERIALIZE_OUTPUT_ROUTING_KEY,
        body=simplejson.dumps({"type": "file", "location": publish_file_path }),
        properties=pika.BasicProperties(content_type="text/plain",
            delivery_mode=2
        )
    )


def serialize(data, name="object"):
    """ Serializes dictionary to xml.
    """
    content_elem = Element("contenttype")
    content_elem.attrib["name"] = name 
    _serialize(content_elem, data)
    tree = ElementTree(content_elem)
    f = StringIO()
    tree.write(f, "UTF-8")
    return f.getvalue()


def _serialize(parent_elem, data):
    if isinstance(data, (list, tuple)):
        _serialize_list(parent_elem, data)
    elif isinstance(data, dict):
        _serialize_dict(parent_elem, data)
    else:
        parent_elem.attrib["name"] = parent_elem.tag
        parent_elem.tag = "field"
        parent_elem.text = unicode(data)


def _serialize_list(parent_elem, data_list):
    for i in data_list:
        item_elem = Element(naming.singular(parent_elem.tag))
        parent_elem.append(item_elem)
        _serialize(item_elem, i)


def _serialize_dict(parent_elem, data_dict):
    if data_dict.has_key("displayAs"):
        parent_elem.tag = "field"
        parent_elem.attrib["name"] = data_dict.get("name")
        parent_elem.attrib["displayAs"] = data_dict.get("displayAs")
        parent_elem.text = unicode(data_dict.get("value"))
        return
    for k, v in data_dict.iteritems():
        key_elem = Element(k)
        parent_elem.append(key_elem)
        _serialize(key_elem, v)

#notifications setup for serialization
SERIALIZE_QUEUE = "bungeni_serialization_queue"
SERIALIZE_EXCHANGE = "bungeni_serialization_exchange"
SERIALIZE_ROUTING_KEY = "bungeni_serialization"
SERIALIZE_OUTPUT_QUEUE = "bungeni_serialization_output_queue"
SERIALIZE_OUTPUT_EXCHANGE = "bungeni_serialization_output_exchange"
SERIALIZE_OUTPUT_ROUTING_KEY = "bungeni_serialization_output"

def serialization_notifications_callback(channel, method, properties, body):
    obj_data = simplejson.loads(body)
    obj_type = obj_data.get("obj_type")
    domain_model = getattr(domain, obj_type, None)
    #!+SESSIONS(mb, aug-2012) investigate why on ObjectCreatedEvent,
    #some objects cannot be queried
    if domain_model:
        #!+TRANSACTIONS(mb, Aug-2012) Works around timing with transaction
        # commits. Messages are fired off to rabbitmq in the middle of a zope
        # transaction before any db changes are persited. As a result callbacks
        # access stale data.
        # Fix is upcoming - amqp messages should be sent as a post-commit hook
        # on a zope transaction.
        log.warn("Sleeping for 10s (let zope transaction commit)")
        time.sleep(10)
        obj_key = valueKey(obj_data.get("obj_key"))
        session = Session()
        obj = session.query(domain_model).get(obj_key)
        if obj:
            publish_to_xml(obj)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            log.error("Could not query object of type %s with key %s. "
                "Requeuing message",
                domain_model, obj_key
            )
            #this might be due to an unsaved instance issue see note above
            channel.basic_reject(delivery_tag=method.delivery_tag,
                requeue=True
            )
        session.close()
    else:
        log.error("Failed to get class in bungeni.models.domain named %s",
            obj_type
        )

def serialization_worker():
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(serialization_notifications_callback,
                          queue=SERIALIZE_QUEUE)
    channel.start_consuming()

@register.handler(adapts=(IWorkflowed, IObjectCreatedEvent))
@register.handler(adapts=(IWorkflowed, IObjectModifiedEvent))
def queue_object_serialization(obj, event):
    """Send a message to the serialization queue for non-draft documents
    """
    wf_state = None
    try:
        wfc = IWorkflowController(obj)
        wf_state = wfc.state_controller.get_state()
    except InvalidStateError:
        log.error("Could not get workflow state for object %s.", obj)
        return
    if wf_state and (
        wfc.state_controller.get_status() in 
        wfc.workflow.get_state_ids(tagged=["private"], restrict=False)):
        return
    unproxied = removeSecurityProxy(obj)
    mapper = object_mapper(unproxied)
    primary_key = mapper.primary_key_from_instance(unproxied)
    #!+CAPI(mb, Aug-2012) capi lookup in as at r9707 fails for some keys
    #e.g. get_type_info(instance).workflow_key resolves while 
    #get_type_info(same_workflow_key) raises KeyError
    message = {
        "obj_key": primary_key,
        "obj_type": unproxied.__class__.__name__
    }
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.basic_publish(
        exchange=SERIALIZE_EXCHANGE,
        routing_key=SERIALIZE_ROUTING_KEY,
        body=simplejson.dumps(message),
        properties=pika.BasicProperties(content_type="text/plain",
            delivery_mode=2
        )
    )

def serialization_notifications():
    """Set up bungeni serialization worker as a daemon.
    """
    mq_utility = zope.component.getUtility(IMessageQueueConfig)
    connection = get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    #create exchange
    channel.exchange_declare(exchange=SERIALIZE_EXCHANGE,
        type="fanout", durable=True)
    channel.queue_declare(queue=SERIALIZE_QUEUE, durable=True)
    channel.queue_bind(queue=SERIALIZE_QUEUE,
       exchange=SERIALIZE_EXCHANGE,
       routing_key=SERIALIZE_ROUTING_KEY)
    #xml outputs channel and queue
    channel.exchange_declare(exchange=SERIALIZE_OUTPUT_EXCHANGE,
        type="direct", passive=False)
    channel.queue_declare(queue=SERIALIZE_OUTPUT_QUEUE, 
        durable=True, exclusive=False, auto_delete=False)
    channel.queue_bind(queue=SERIALIZE_OUTPUT_QUEUE,
        exchange=SERIALIZE_OUTPUT_EXCHANGE,
        routing_key=SERIALIZE_OUTPUT_ROUTING_KEY)
    for i in range(mq_utility.get_number_of_workers()):
        task_thread = Thread(target=serialization_worker)
        task_thread.daemon = True
        task_thread.start()
