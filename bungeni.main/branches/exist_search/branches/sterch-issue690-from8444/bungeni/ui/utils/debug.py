# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Debug utilities

recommended usage:
from bungeni.ui.utils import debug

$Id$
"""
log = __import__("logging").getLogger("bungeni.ui.utils.debug")


from zope import component
from zope import interface
import zope.event


def interfaces(obj):
    """Dump out list of interfaces for an object..."""
    return "\n".join(["",
        #interfaces_implementedBy_class_for(obj),
        interfaces_providedBy(obj),
        interfaces_directlyProvidedBy(obj),
    ])
def interfaces_implementedBy_class_for(obj):
    """Dump out list of interfaces implementedBy an object's class."""
    return """  interfaces implementedBy %s:
    %s""" % (obj.__class__, 
          "\n    ".join(
          ["%s %s"%(i, id(i)) for i in interface.implementedBy(obj.__class__)]
          or [ "</>" ] ))
def interfaces_providedBy(obj):
    """Dump out list of interfaces providedBy an object."""
    return """  interfaces providedBy %s:
    %s""" % (repr(obj), 
          "\n    ".join(["%s %s"%(i, id(i)) for i in interface.providedBy(obj)]
          or [ "</>" ] ))
def interfaces_directlyProvidedBy(obj):
    """Dump out list of interfaces directlyProvidedBy an object."""
    return """  interfaces directlyProvidedBy %s:
    %s""" % (repr(obj), 
          "\n    ".join(["%s %s"%(i, id(i)) for i in interface.directlyProvidedBy(obj)]
          or [ "</>" ] ))


def location_stack(obj):
    """Dump out __parent__ stack for an object."""
    ps = []
    def _ps(ob):
        if ob is not None:
            _ps(ob.__parent__)
            ps.append("%s [[%s]]" % (ob, getattr(ob, "context", "</>")))
        else:
            ps.append("None")
    _ps(obj)
    return """  parent [[context]] stack for %s:
    %s""" % (obj, "\n    ".join(ps))


# exception logging

import traceback
def log_exc_info(exc_info, log_handler=log.error):
    """Traceback log an exception.
    exc_info: the 3-tuple as returned by sys.get_exc_info()
        the client is required to call sys.get_exc_info() itself
    log_handler: to allow logging via the caller's logger, 
        but defaults to bungeni.ui.utils.log.error
    """
    cls, exc, tb = exc_info
    log_handler("""\n%s""" % (traceback.format_exc(tb)))

def log_exc(exc_info, log_handler=log.error):
    """Short log of an exception.
    exc_info: the 3-tuple as returned by sys.get_exc_info()
        the client is required to call sys.get_exc_info() itself
    log_handler: to allow logging via the caller's logger, 
        but defaults to bungeni.ui.utils.log.error
        
    Sample usage:
        import sys
        try: ...
        except (AnError, AnotherError, ... ):
            debug.log_exc(sys.exc_info(), log_handler=log.info)
    """
    cls, exc, tb = exc_info
    log_handler(""" [%s] %s""" % (cls.__name__, exc))

def log_io(f):
    """Debugging decorator utility, print out all input parameters and the 
    return value of the decorated.
    """
    name = f.__name__
    def _f(*args, **kw):
        ret = f(*args, **kw)
        print " ** %s: %s, %s -->> %s" % (name, args, kw, ret)
        return ret
    return _f

# events 

#from ore.wsgiapp.interfaces import WSGIApplicationCreatedEvent
#@component.adapter(WSGIApplicationCreatedEvent)
#def subscribe_log_all_events(event):
#    log_event(event)
#    zope.event.subscribers.append(log_event)

def subscribe_log_all_events():
    """Subscribe log_event handler, to log all events."""
    zope.event.subscribers.append(log_event)

def log_event(event):
    """Handler to log an event."""
    log.debug(" [log_event] %s" % event)

# string comparison

import difflib
def unified_diff(old_str, new_str, old_name="OLD", new_name="NEW"):
    """Return a unified diff of two strings.
    """
    return "".join(difflib.unified_diff(
                old_str.splitlines(1), 
                new_str.splitlines(1), 
                fromfile=old_name, 
                tofile=new_name))


