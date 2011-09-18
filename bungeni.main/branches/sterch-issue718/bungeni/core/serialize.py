# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

""" Utilities to serialize objects to XML
"""

from StringIO import StringIO
from xml.etree.cElementTree import Element, ElementTree
import traceback
import sys
from zope.security.proxy import removeSecurityProxy
from bungeni.core.interfaces import IVersioned
from sqlalchemy.orm import RelationshipProperty, class_mapper 
from bungeni.ui.utils import queries, statements
import collections
from sqlalchemy.orm.collections import InstrumentedList


custom = {
    "signatory": "signatories",
}

def singular(pname):
    """Get the english singular of (plural) name.
    """
    for sname in custom:
        if custom[sname] == pname:
            return sname
    if pname.endswith("ses"):
        return pname[:-2]
    if pname.endswith("s"):
        return pname[:-1]
    return pname

def serialize(data):
    content_elem = Element('object')
    _serialize(content_elem, data)
    tree = ElementTree(content_elem)
    f = StringIO()
    tree.write(f, 'UTF-8')
    return f.getvalue()

def _serialize(parent_elem, data):
    if isinstance(data, (list, tuple)):
        _serialize_list(parent_elem, data)
    elif isinstance(data, dict):
        _serialize_dict(parent_elem, data)
    else:
        if len(str(data))>1500:
            parent_elem.text = 'file_here'
        else:
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
    result = {}
    obj = removeSecurityProxy(obj)
    try:
        for name in include:
            value = getattr(obj, name)
            if isinstance(value, collections.Iterable):
                res = []
                for item in value.values():
                    res.append(obj2dict(item, 0))
                result[name] = res
            else:
                result[name] = value
            
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
                        result[property.key].append(obj2dict(item, depth-1, parent=obj,include=[],exclude=['changes',]))
                else:
                    result[property.key] = obj2dict(value, depth-1, parent=obj,include=[],exclude=['changes',])
            else:
                if isinstance(property, RelationshipProperty):
                    continue
                result[property.key] = value
    except:
        traceback.print_exception(*sys.exc_info())
    return result