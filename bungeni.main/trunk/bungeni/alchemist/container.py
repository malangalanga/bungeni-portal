# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni Alchemist container

$Id$
"""
log = __import__("logging").getLogger("bungeni.alchemist")

from ore.alchemist.container import valueKey
from ore.alchemist.container import contained
from ore.alchemist.container import PartialContainer

#

from sqlalchemy import orm
from zope.security import proxy

def stringKey(obj):
    """Replacement of ore.alchemist.container.stringKey
    
    The difference is that here the primary_key is not determined by 
    sqlalchemy.orm.mapper.primary_key_from_instance(obj) but by doing the 
    logically equivalent (but a little more laborious) 
    [ getattr(instance, c.name) for c in mapper.primary_key ].
    
    This is because, in some hard-to-debug cases, the previous was returning 
    None to all pk values e.g. for objects on which checkPermission() has not
    been called. Using this version, the primary_key is correctly determined
    irrespective of whether checkPermission() had previously been called on
    the object.
    """
    unproxied = proxy.removeSecurityProxy(obj)
    mapper = orm.object_mapper(unproxied)
    #primary_key = mapper.primary_key_from_instance(unproxied)
    identity_values = [ getattr(unproxied, c.name) for c in mapper.primary_key ]
    identity_key = '-'.join(map(str, identity_values))
    return "obj-%s" % (identity_key)

