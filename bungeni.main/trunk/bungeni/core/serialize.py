# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

""" Utilities to serialize objects to XML
"""

from zope.security.proxy import removeSecurityProxy
from sqlalchemy.orm import RelationshipProperty, class_mapper

from bungeni.core.workflow.states import get_object_state_rpm, get_object_version_state_rpm
from bungeni.models.schema import singular
from bungeni.alchemist.container import stringKey
from bungeni.models.interfaces import IAuditable, IVersionable, IAttachmentable

import os
import collections
from StringIO import StringIO
from zipfile import ZipFile
from xml.etree.cElementTree import Element, ElementTree


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

def get_permissions_dict(permissions):
    results= []
    for x in permissions:
        results.append({"role":x[2], 
                        "permission":x[1], 
                        "setting":x[0] and "Allow" or "Deny"})
    return results


def publish_to_xml(context, type="", include=None):
    """ Generates XML for object and saves it to the file. If object contains
        attachments - XML is saved in zip archive with all attached files. 
    """
    
    if include is None:
        include = []
    
    context = removeSecurityProxy(context)
    
    if IVersionable.implementedBy(context.__class__):
        include.append("versions")
    if IAuditable.implementedBy(context.__class__):
        include.append("event")
    
    data = obj2dict(context,1,parent=None,include=include,
                    exclude=["file_data", "image", "logo_data","event_item"])
    if type=="":
        type = getattr(context,"type", None)
        
        permissions = get_object_state_rpm(context).permissions
        data["permissions"]= get_permissions_dict(permissions)

    assert type, "%s has no 'type' field. Use 'type' function parameter." % context.__class__
                
    files = []
    path = os.path.join(setupStorageDirectory(), type)
    if not os.path.exists(path):
        os.makedirs(path)
        
    file_path = os.path.join(path,stringKey(context))
    files.append(file_path+".xml") 
    with open(file_path+".xml","w") as file:
        file.write(serialize(data, name=type))
    
    if IAttachmentable.implementedBy(context.__class__):
        attached_files = getattr(context, "attached_files", None)
        if attached_files:
            for attachment in attached_files:
                attachment_path = os.path.join(path, attachment.file_name)
                files.append(attachment_path)
                with open(os.path.join(path, attachment.file_name), "wb") as file:
                    file.write(attachment.file_data)
            zip = ZipFile(file_path+".zip", "w")
            for file in files:
                zip.write(file, os.path.split(file)[-1])
                os.remove(file)
            zip.close()    


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
        item_elem = Element(singular(parent_elem.tag))
        parent_elem.append(item_elem)
        _serialize(item_elem, i)


def _serialize_dict(parent_elem, data_dict):
    for k, v in data_dict.iteritems():
        key_elem = Element(k)
        parent_elem.append(key_elem)
        _serialize(key_elem, v)


def obj2dict(obj, depth, parent=None, include=[], exclude=[]):
    """ Returns dictionary representation of an object.
    """
    result = {}
    obj = removeSecurityProxy(obj)
    
    # Get additional attributes
    for name in include:
        value = getattr(obj, name, None)
        if value is None:
            continue
        if not name.endswith("s"): name += "s"
        if isinstance(value, collections.Iterable):
            res = []
            for item in value.values():
                i = obj2dict(item, 0)
                if name == "versions":
                    permissions = get_object_version_state_rpm(item).permissions
                    i["permissions"] = get_permissions_dict(permissions)
                res.append(i)
            result[name] = res
        else:
            result[name] = value
            
    # Get mapped attributes
    for property in class_mapper(obj.__class__).iterate_properties:
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
                    result[property.key].append(obj2dict(item, depth-1, 
                                                         parent=obj,include=[],
                                                         exclude=exclude+["changes",]))
            else:
                result[property.key] = obj2dict(value, depth-1, parent=obj,
                                                include=[],exclude=exclude+["changes",])
        else:
            if isinstance(property, RelationshipProperty):
                continue
            result[property.key] = value
    return result