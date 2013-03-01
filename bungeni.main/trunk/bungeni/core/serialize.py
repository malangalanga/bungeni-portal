# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

""" Utilities to serialize objects to XML

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.serialize")

import os
import math
from StringIO import StringIO
from zipfile import ZipFile
from threading import Thread, Timer

from xml.etree.cElementTree import Element, ElementTree
from tempfile import NamedTemporaryFile as tmp
import simplejson

import zope.component
import zope.app.component
import zope.security
import zope.event
from zope.lifecycleevent import IObjectModifiedEvent, IObjectCreatedEvent
from bungeni.core.testing import create_participation

from sqlalchemy.orm import class_mapper, object_mapper

from ore.alchemist.container import valueKey
from bungeni.alchemist.container import stringKey
from bungeni.alchemist import Session
from bungeni.alchemist.interfaces import IAlchemistContent
from bungeni.core.workflow.states import (get_object_state_rpm, 
    get_head_object_state_rpm
)
from bungeni.core.interfaces import (
    IMessageQueueConfig, 
    NotificationEvent, 
    IVersionCreatedEvent
)
from bungeni.core.workflow.interfaces import (IWorkflow, IStateController,
    IWorkflowed, IWorkflowController, InvalidStateError
)
import bungeni.core

from bungeni.models import interfaces, domain, settings
from bungeni.models.utils import is_column_binary
from bungeni.utils import register, naming, common
from bungeni.ui.interfaces import IVocabularyTextField
from bungeni.capi import capi

import transaction
import pika

# timer delays in setting up serialization workers
INITIAL_DELAY = 10
MAX_DELAY = 300
TIMER_DELAYS = {
    "serialize_setup": INITIAL_DELAY
}
                
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
        try:
            os.mkdir(store_dir)
        except OSError:
            # assume some other code created directory
            assert(os.path.exists(store_dir))
    
    return store_dir


def get_origin_parliament(context):
    """get the parliament applicable to this object
    """
    chamber_id = None
    group_id = getattr(context, "group_id", None)
    if group_id:
        group = Session().query(domain.Group).get(group_id)
        while group.parent_group_id is not None:
            group = Session().query(domain.Group).get(group.parent_group_id)
        if isinstance(group, domain.Parliament):
            chamber_id = group.group_id
    else:
        chamber_id = getattr(context, "parliament_id", None)
    if not chamber_id:
        if hasattr(context, "head_id"):
            return get_origin_parliament(context.head)
    return chamber_id

def publish_to_xml(context):
    """Generates XML for object and saves it to the file. If object contains
    attachments - XML is saved in zip archive with all attached files. 
    """

    #create a fake interaction to ensure items requiring a participation
    #are serialized 
    #!+SERIALIZATION(mb, Jan-2013) review this approach
    try:
        zope.security.management.getInteraction()
    except zope.security.interfaces.NoInteraction:
        principal = zope.security.testing.Principal('user', 'manager', ())
        zope.security.management.newInteraction(create_participation(principal))

    include = []
    # list of files to zip
    files = []
    # data dict to be published
    data = {}
    
    context = zope.security.proxy.removeSecurityProxy(context)
    
    if interfaces.IFeatureVersion.providedBy(context):
        include.append("versions")
    if interfaces.IFeatureAudit.providedBy(context):
        include.append("event")
    
    exclude = ["data", "event", "attachments", "changes"]
    
    # include binary fields and include them in the zip of files for this object
    for column in class_mapper(context.__class__).columns:
        if is_column_binary(column):
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
                attached_file.flush()
                attached_file.close()
                files.append(attached_file.name)
                attachment_dict["saved_file"] = os.path.basename(
                    attached_file.name
                )
                data["attachments"].append(attachment_dict)

    #add explicit origin chamber for this object (used to partition data in
    #if more than one parliament exists)
    data["origin_parliament"] = get_origin_parliament(context)
    
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
        # write the xml
        zip_file.write(temp_xml.name, "%s.xml" % os.path.basename(file_path))
        zip_file.close()
        #placed remove after zip_file.close !+ZIP_FILE_CRC_FAILURE
        os.remove(temp_xml.name) 

    else:
        # save serialized xml to file
        with open("%s.xml" % (file_path), "w") as xml_file:
            xml_file.write(serialize(data, name=obj_type))
            xml_file.close()

    # publish to rabbitmq outputs queue
    connection = bungeni.core.notifications.get_mq_connection()
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
    
    #clean up - remove any files if zip was created
    if files:
        prev_xml_file = "%s.%s" %(file_path, "xml")
        if os.path.exists(prev_xml_file):
            os.remove(prev_xml_file)


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
        if not isinstance(data, unicode):
            data = unicode(data)
        parent_elem.text = data


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
        data = data_dict.get("value")
        if not isinstance(data, unicode):
            data = unicode(data)
        parent_elem.text = data
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

SERIALIZE_FAILURE_TEMPLATE = """
There was an error while serializing a document: 

Object:
%(obj)s

Original AMQP message: 
%(message)s

Error:
%(error)s

- Bungeni
"""

def notify_serialization_failure(template, **kw):
    email_settings = settings.EmailSettings(common.get_application())
    recipients = [ email_settings.default_sender ]    
    if template:
        body_text = template % kw
    else:
        body_text = kw.get("body")
    msg_event = NotificationEvent({
        "recipients": recipients,
        "body": body_text, 
        "subject": kw.get("subject", "Serialization Failure")
    })
    zope.event.notify(msg_event)


def serialization_notifications_callback(channel, method, properties, body):
    obj_data = simplejson.loads(body)
    obj_type = obj_data.get("obj_type")
    domain_model = getattr(domain, obj_type, None)
    if domain_model:
        obj_key = valueKey(obj_data.get("obj_key"))
        session = Session()
        obj = session.query(domain_model).get(obj_key)
        if obj:
            try:
                publish_to_xml(obj)
            except Exception, e:
                notify_serialization_failure(SERIALIZE_FAILURE_TEMPLATE,
                    obj=obj, message=obj_data, error=e
                )
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            log.error("Could not query object of type %s with key %s. "
                "Check database records - Rejecting message.",
                domain_model, obj_key
            )
            #Reject the message
            channel.basic_reject(delivery_tag=method.delivery_tag,
                requeue=False
            )
        session.close()
    else:
        log.error("Failed to get class in bungeni.models.domain named %s",
            obj_type
        )

def serialization_worker():
    connection = bungeni.core.notifications.get_mq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(serialization_notifications_callback,
                          queue=SERIALIZE_QUEUE)
    channel.start_consuming()


class SerializeThread(Thread):
    """This thread will respawn after n seconds if it crashes
    """
    is_running = True
    daemon = True
    def run(self):
        while self.is_running:
            try:
                super(SerializeThread, self).run()
            except Exception, e:
                log.error("Exception in thread %s: %s", self.name, e)
                delay = TIMER_DELAYS[self.name]
                if delay > MAX_DELAY:
                    num_attempts = int(math.log((delay/10), 2));
                    log.error("Giving up re-spawning serialization " 
                        "worker after %d seconds (%d attempts).", 
                        delay, num_attempts
                    )
                    notify_serialization_failure(None,
                        subject="Notice - Bungeni Serialization Workers",
                        body="""Unable to restart serialization worker.
                    Please check the Bungeni logs."""
                    )
                else:
                    log.info("Attempting to respawn serialization "
                        "consumer in %d seconds", delay
                    )
                    next_delay = delay * 2
                    timer = Timer(delay, init_thread, [], 
                        {"delay": next_delay })
                    timer.daemon = True
                    timer.start()
                self.is_running = False
                del TIMER_DELAYS[self.name]

def init_thread(*args, **kw):
    log.info("Initializing serialization consumer thread...")
    delay = kw.get("delay", INITIAL_DELAY)
    task_thread = SerializeThread(target=serialization_worker)
    task_thread.start()
    TIMER_DELAYS[task_thread.name] = delay
    

def batch_serialize(type_key="*"):
    """Serialize all objects of `type_key` or all types if with a
    wildcard(*) as the type key.
    """
    #keep count of serialized objects for feedback
    serialized_count = 0
    #list of domain classes to be serialized
    domain_models = []
    if type_key == "*":
        for (type_key, info) in capi.iter_type_info():
            if info.workflow:
                domain_models.append(info.domain_model)
    else:
        info = capi.get_type_info(type_key)
        if info.workflow:
            domain_models.append(info.domain_model)
    session = Session()
    for domain_model in domain_models:
        objects = session.query(domain_model).all()
        map(queue_object_serialization, objects)
        serialized_count += len(objects)
    return serialized_count
    

@register.handler(adapts=(IVersionCreatedEvent,))
def serialization_version_event_handler(event):
    """Queues workflowed objects when a version is created.
    """
    # we only want to serialize manually created versions
    if event.object.procedure == "m":
        queue_object_serialization(event.object.head)

@register.handler(adapts=(IWorkflowed, IObjectCreatedEvent))
@register.handler(adapts=(IWorkflowed, IObjectModifiedEvent))
def serialization_event_handler(obj, event):
    """queues workflowed objects when created or modified"""
    queue_object_serialization(obj)

@register.handler(adapts=(IAlchemistContent, IObjectCreatedEvent))
@register.handler(adapts=(IAlchemistContent, IObjectModifiedEvent))
def serialization_event_handler_non_wf(obj, event):
    """queues serialization of workflowed parent (if any)"""
    #!+SERIALIZATION(mb, Jan-2013) Might change how changes are bubbled up
    if not IWorkflowed.providedBy(obj):
        # workflowed types will be handled by serialize_event_handler
        wf_parent = obj
        while not IWorkflowed.providedBy(wf_parent):
            wf_parent = (wf_parent.__parent__ 
                if hasattr(wf_parent, "__parent__") else None)
            if not wf_parent:
                break
        if wf_parent:
            queue_object_serialization(wf_parent)

def queue_object_serialization(obj):
    """Send a message to the serialization queue for non-draft documents
    """
    connection = bungeni.core.notifications.get_mq_connection()
    if not connection:
        log.warn("Could not get rabbitmq connection. Will not send "
            "AMQP message for this change."
        )
        log.warn("Publishing XML directly - this will slow things down")
        try:
            publish_to_xml(obj)
        except Exception, e:
            notify_serialization_failure(SERIALIZE_FAILURE_TEMPLATE,
                obj=obj, message="", error=e
            )
            notify_serialization_failure(None, 
                body="Failed to find running RabbitMQ",
                subject="Notice - RabbitMQ"
            )
        notify_serialization_failure(None, 
            body="Failed to find running RabbitMQ",
            subject="Notice - RabbitMQ"
        )
        return
    wf_state = None
    try:
        wfc = IWorkflowController(obj)
        wf_state = wfc.state_controller.get_state()
    except InvalidStateError:
        #this is probably a draft document - skip queueing
        log.warning("Could not get workflow state for object %s. "
            "State: %s", obj, wf_state)
        return
    unproxied = zope.security.proxy.removeSecurityProxy(obj)
    mapper = object_mapper(unproxied)
    primary_key = mapper.primary_key_from_instance(unproxied)
    #!+CAPI(mb, Aug-2012) capi lookup in as at r9707 fails for some keys
    #e.g. get_type_info(instance).workflow_key resolves while 
    #get_type_info(same_workflow_key) raises KeyError
    message = {
        "obj_key": primary_key,
        "obj_type": unproxied.__class__.__name__
    }
    kwargs = dict(
        exchange=SERIALIZE_EXCHANGE,
        routing_key=SERIALIZE_ROUTING_KEY,
        body=simplejson.dumps(message),
        properties=pika.BasicProperties(content_type="text/plain",
            delivery_mode=2
        )
    )
    txn = transaction.get()
    txn.addAfterCommitHook(bungeni.core.notifications.post_commit_publish, (), kwargs)
 
    
def serialization_notifications():
    """Set up bungeni serialization worker as a daemon.
    """
    mq_utility = zope.component.getUtility(IMessageQueueConfig)
    connection = bungeni.core.notifications.get_mq_connection()
    if not connection:
        #delay
        delay = TIMER_DELAYS["serialize_setup"]
        if delay > MAX_DELAY:
            log.error("Could not set up amqp workers - No rabbitmq " 
            "connection found after %d seconds.", delay)
        else:
            log.info("Attempting to setup serialization AMQP consumers "
                "in %d seconds", delay
            )
            timer = Timer(TIMER_DELAYS["serialize_setup"],
                serialization_notifications
            )
            timer.daemon = True
            timer.start()
            TIMER_DELAYS["serialize_setup"] *= 2
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
        init_thread()




# serialization utilities

import collections
import zope.component
import zope.schema as schema
from zope.i18n import translate
from zope.dublincore.interfaces import IDCDescriptiveProperties
from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from bungeni.alchemist import utils
from bungeni.alchemist.interfaces import IAlchemistContainer


def get_permissions_dict(permissions):
    results= []
    for x in permissions:
        # !+XML pls read the styleguide
        results.append({"role": x[2], 
            "permission": x[1], 
            "setting": x[0] and "Allow" or "Deny"})
    return results

def obj2dict(obj, depth, parent=None, include=[], exclude=[], lang=None):
    """ Returns dictionary representation of a domain object.
    """
    if lang is None:
        lang = getattr(obj, "language", capi.default_language)
    result = {}
    obj = zope.security.proxy.removeSecurityProxy(obj)
    descriptor = None
    if IAlchemistContent.providedBy(obj):
        try:
            descriptor = utils.get_descriptor(obj)
        except KeyError:
            log.error("Could not get descriptor for IAlchemistContent %r", obj)
    
    # Get additional attributes
    for name in include:
        value = getattr(obj, name, None)
        if value is None:
            continue
        if not name.endswith("s"):
            name += "s"
        if isinstance(value, collections.Iterable):
            res = []
            # !+ allowance for non-container-api-conformant alchemist containers
            if IAlchemistContainer.providedBy(value):
                value = value.values()
            for item in value:
                i = obj2dict(item, 0, lang=lang)
                if name == "versions":
                    permissions = get_head_object_state_rpm(item).permissions
                    i["permissions"] = get_permissions_dict(permissions)
                res.append(i)
            result[name] = res
        else:
            result[name] = value
    
    # Get mapped attributes
    mapper = class_mapper(obj.__class__)
    for property in mapper.iterate_properties:
        if property.key in exclude:
            continue
        value = getattr(obj, property.key)
        if value == parent:
            continue
        if value is None:
            continue
        
        if isinstance(property, RelationshipProperty) and depth > 0:
            if isinstance(value, collections.Iterable):
                result[property.key] = []
                for item in value:
                    result[property.key].append(obj2dict(item, 1, 
                            parent=obj,
                            include=[],
                            exclude=exclude + ["changes"],
                            lang=lang
                    ))
            else:
                result[property.key] = obj2dict(value, depth-1, 
                    parent=obj,
                    include=[],
                    exclude=exclude + ["changes"],
                    lang=lang
                )
        else:
            if isinstance(property, RelationshipProperty):
                continue
            elif isinstance(property, ColumnProperty):
                columns = property.columns
                if len(columns) == 1:
                    if is_column_binary(columns[0]):
                        continue
            if descriptor:
                columns = property.columns
                is_foreign = False
                if len(columns) == 1:
                    if len(columns[0].foreign_keys):
                        is_foreign = True
                if (not is_foreign) and (property.key in descriptor.keys()):
                    field = descriptor.get(property.key)
                    if (field and field.property and
                        (schema.interfaces.IChoice.providedBy(field.property)
                            or IVocabularyTextField.providedBy(field.property))
                        ):
                                factory = (field.property.vocabulary or 
                                    field.property.source
                                )
                                if factory is None:
                                    vocab_name = getattr(field.property, 
                                        "vocabularyName", None)
                                    factory = zope.component.getUtility(
                                        schema.interfaces.IVocabularyFactory,
                                        vocab_name
                                    )
                                # !+VOCABULARIES(mb, aug-2012)some vocabularies
                                # expect an interaction to generate values
                                # todo - update these vocabularies to work 
                                # with no request e.g. in notification threads
                                display_name = None
                                try:
                                    vocabulary = factory(obj)                             
                                    term = vocabulary.getTerm(value)
                                    if lang:
                                        if hasattr(factory, "vdex"):
                                            display_name = (
                                                factory.vdex.getTermCaption(
                                                factory.getTermById(value), 
                                                lang
                                            ))
                                        else:
                                            display_name = translate(
                                                (term.title or term.value),
                                                target_language=lang,
                                                domain="bungeni"
                                            )
                                    else:
                                        display_name = term.title or term.value
                                except zope.security.interfaces.NoInteraction:
                                    log.error("This vocabulary %s expects an"
                                        "interaction to generate terms.",
                                        factory
                                    )
                                    # try to use dc adapter lookup
                                    try:
                                        _prop = mapper.get_property_by_column(
                                            property.columns[0])
                                        _prop_value = getattr(obj, _prop.key)
                                        dc = IDCDescriptiveProperties(
                                            _prop_value, None)
                                        if dc:
                                            display_name = (
                                                IDCDescriptiveProperties(
                                                    _prop_value).title
                                            )
                                    except KeyError:
                                        log.warn("No display text found for %s" 
                                            " on object %s. Unmapped in orm.",
                                            property.key, obj
                                        )
                                except Exception, e:
                                    log.error("Could not instantiate"
                                        " vocabulary %s. Exception: %s",
                                        factory, e
                                    )
                                finally:
                                    # fallback we cannot look up vocabularies/dc
                                    if display_name is None:
                                        if not isinstance(value, unicode):
                                            display_name = unicode(value)
                                if display_name is not None:
                                    result[property.key] = dict(
                                        name=property.key,
                                        value=value,
                                        displayAs=display_name
                                    )
                                    continue
            result[property.key] = value
    
    for prop_name, prop_type in obj.__class__.extended_properties:
        try:
            result[prop_name] = getattr(obj, prop_name)
        except zope.security.interfaces.NoInteraction:
            log.error("Extended property %s requires an interaction.",
                prop_name)

    
    # any additional attributes - this allows us to capture any derived attributes
    if IAlchemistContent.providedBy(obj):
        seen_keys = ( [ prop.key for prop in mapper.iterate_properties ] + 
            include + exclude)
        try:
            domain_schema = utils.get_derived_table_schema(type(obj))
            known_names = [ k for k, d in 
                domain_schema.namesAndDescriptions(all=True) ]
            extra_properties = set(known_names).difference(set(seen_keys))
            for prop_name in extra_properties:
                try:
                    result[prop_name] = getattr(obj, prop_name)
                except zope.security.interfaces.NoInteraction:
                    log.error("Attribute %s requires an interaction.",
                        prop_name)

        except KeyError:
            log.warn("Could not find table schema for %s", obj)
    
    return result


