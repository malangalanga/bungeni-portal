# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Misc utilities

recommended usage:
from bungeni.utils import misc

$Id$
"""
log = __import__("logging").getLogger("bungeni.utils.misc")

import os


# xml attr values

def xml_attr_bool(elem, attr_name, default=False):
    return as_bool(strip_none(elem.get(attr_name)) or str(default))

def xml_attr_int(elem, attr_name, default=None):
    value = strip_none(elem.get(attr_name)) or default
    if value is not None:
        value = int(value)
    return value

def xml_attr_str(elem, attr_name, default=None):
    return strip_none(elem.get(attr_name)) or default


# string / conversion / comparison

def strip_none(s):
    """Ensure non-empty whitespace-stripped string, else None.
    """
    if s is not None:
        return s.strip() or None
    return None

def as_bool(s):
    """(s:str) -> bool 
    Cast case-insensitive & stripped strings "true" or "false" to boolean.
    Other string variations give TypeError.
    """
    _s = s.strip().lower()
    if _s == "true":
        return True
    elif _s == "false":
        return False
    raise TypeError("Invalid bool: %s" % s)


import datetime, re
def date_from_iso8601(s):
    return datetime.date(*map(int, re.split("[^\d]", s)))

def named_repr(obj, name):
    return "<%s.%s '%s' object at %s>" % (
        obj.__module__, type(obj).__name__, name, hex(id(obj)))


# cache

def cached_property(f):
    """Cached property decorator, caching on bound instance and auto-deriving 
    the cache attribute name from the original function name.
    
    Note: if f is itself a decorated func, the name of original function must be
    correctly bubbled up to it i.e. the decorated renamed to original func name.
    """
    attr_name = "_cached_%s" % (f.__name__)
    def fget(instance):
        if not hasattr(instance, attr_name):
            setattr(instance, attr_name, f(instance))
        return getattr(instance, attr_name)
    return property(fget)


# list

def get_keyed_item(seq, value, key="name"):
    """Get the first item in the sequence that has a {key} entry set to {value}.
    """
    for s in seq:
        if s[key] == value:
            return s
        
def replace_keyed_item(seq, replacement_item, key="name"):
    """Replace the first item in the sequence whose {key} value is same as 
    replacement_item[{key}].
    """
    for s in seq:
        if s[key] == replacement_item[key]:
            seq[seq.index(s)] = replacement_item
            return
    raise LookupError("No matching item [%s=%r] found in seq: %s" % (
        key, replacement_item[key], seq))


# object

class bunch(dict):
    """A dictionary-bunch of values, with convenient dotted access.
    Limitation: keys must be valid object attribute names.
    Inspiration: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
    """
    def __init__(self, **kwds):
        dict.__init__(self, kwds)
        self.__dict__ = self

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self

    def update_from_object(self, obj, no_underscored=True):
        """ (obj:object) -> None
        Sets each key in dir(obj) as key=getattr(object, key) in self.
        If no_underscored, then exclude "private" (leading "_") and 
        "protected" (leading "__") attributes.
        """
        for name in dir(obj):
            if not (no_underscored and name.startswith("_")):
                self[name] = getattr(obj, name)


# io

def read_file(file_path):
    return open(file_path, "r").read().decode("utf-8")

def check_overwrite_file(file_path, content, log_handler=log.debug):
    """Write content to file_path if necessary (that is if there are changes),
    creating it if does not exist. Log a "diff" to preceding content.
    """
    try:
        log_handler(" *** OVERWRITING file: %s", file_path)
        persisted = read_file(file_path)
    except IOError:
        log_handler(" *** CREATING file: %s", file_path)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        persisted = """<NO-SUCH-FILE path="%s" />\n""" % (file_path)
    # compare with saved file, and re-write if needed
    if persisted != content:
        from bungeni.utils import probing
        log_handler("CHANGES to file:\n%s", 
            probing.unified_diff(persisted, content, file_path, "NEW"))
        open(file_path, "w").write(content.encode("utf-8"))

# 

def describe(funcdesc):
    """
    The describe decorator is used add @describe annotations to 
    functions. This is used in conditions, validations etc to provide
    a extractable and i18n-able description of the function - as these 
    are provided in list boxes in the configuration UI
    """
    def decorate(func):
        setattr(func, "description", funcdesc)
        return func
    return decorate            


# i18n

def setup_i18n_message_factory_translate(domain):
    """Utility to guarantee that env is setup correctly (and mo files compiled)
    prior to fixing an i18n message factory. 
    
    Returns (_, translate) to be used throughout the bungeni app for defining
    i18n literal msgids and for translating them. !+NON_STANDARD_I18N
    """
    # prepare env
    from bungeni.capi import capi
    put_env("zope_i18n_allowed_languages", capi.zope_i18n_allowed_languages)
    put_env("zope_i18n_compile_mo_files", capi.zope_i18n_compile_mo_files)
    
    # get the i18n message factory
    # !+NON_STANDARD_I18N - this is NOT the equivalent of the gettext(msgid) 
    # utility that is within python programs is normally aliased to _().
    import zope.i18n
    import zope.i18nmessageid
    _ = zope.i18nmessageid.MessageFactory(domain)
    
    # define the translate function 
    # !+NON_STANDARD_I18N - this is the equivalent of the gettext.gettext(msgid) 
    # that is what is usually aliased as _() in the local namespace
    def translate(msgid, **kwargs):
        """Translate msgid from catalogs using default domain if none provided.
        
        API: zope.i18n.translate(msgid, domain=None,
                mapping=None, context=None, target_language=None, default=None)
        """
        if kwargs.get("domain", None) is None:
            kwargs["domain"] = domain
        if kwargs.get("target_language", None) is None:
            from bungeni.core.language import get_default_language
            kwargs["target_language"] = get_default_language() or capi.default_language
        return zope.i18n.translate(msgid, **kwargs)
    
    return _, translate


#

def put_env(key, value):
    """Set the the environment variable {key} to {value}
    i.e. use to set os.environ[key].
    
    Wrapper on os.put_env(key, string_value) -- to take care of
    the value string-casting required by os.put_env while still 
    allowing the liberty of data-typing values of capi attributes 
    as needed.
    """
    try:
        os.environ[key] = value
        # OK, value is a string... done.
    except TypeError:
        # putenv() argument 2 must be string, not <...>
        # i.e. value is NOT a string... try string-casting:
        try:
            # some zope code expects sequences to be specified as a 
            # COMMA or SPACE separated STRING, so we first try the value 
            # as a sequence, and serialize it to an environment variable 
            # value as expected by zope
            os.environ[key] = " ".join(value)
        except TypeError:
            # not a sequence, just fallback on repr(value)
            os.environ[key] = repr(value)
            # ensure that the original object value defines a __repr__ 
            # that can correctly re-instantiate the original object
            assert eval(os.environ[key]) == value


# 

def get_bungeni_installation_dir():
    """Get the path to the bungeni installation directory.
    """
    current_dir = __file__
    trailing_file_name = ""
    while trailing_file_name != "src":
        current_dir, trailing_file_name = os.path.split(current_dir)
    return current_dir

