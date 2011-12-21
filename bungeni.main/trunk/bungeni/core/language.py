# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Language Negotiation Utilities

$Id$
$URL$
"""
log = __import__("logging").getLogger("bungeni.core.language")

from zope import interface
from zope.app.zapi import getUtilitiesFor
from zope.publisher.browser import BrowserLanguages
from zope.i18n.negotiator import normalize_lang
from zope.i18n import translate

from locale import getdefaultlocale

from bungeni.core.interfaces import ILanguageProvider
from bungeni.utils.capi import capi
from bungeni.core.translation import get_request_language
from bungeni.ui.utils.common import get_request
from bungeni.utils import register
from ploned.ui.interfaces import ITextDirection


class TranslateUtility(object):
    """
    Factory for translation utilities
    Wraps around `zope.i18n.translate` tied to context(request)
    """
    context = None
    domain = None

    def __init__(self, context, domain="bungeni"):
        self.context = context
        self.domain = domain

    def __call__(self, source_string):
        return translate(source_string, domain=self.domain,
            context=self.context
        )


class BaseLanguageProvider(object):
    interface.implements(ILanguageProvider)

    def __call__(self):
        return normalize_lang(self.getLanguage())

    def getLanguage(self):
        raise NotImplementedError("Inheriting class must implement this")

class SystemLanguage(BaseLanguageProvider):
    WEIGHT = 10

    def getLanguage(self):
        locale = getdefaultlocale()
        try:
            return locale[0]
        except IndexError:
            return None

class ApplicationLanguage(BaseLanguageProvider):
    WEIGHT = 9

    def getLanguage(self):
        return capi.default_language

class BrowserLanguage(BaseLanguageProvider):
    WEIGHT = 8

    def getLanguage(self):
        request = get_request()
        if request is not None:
            browser_langs = BrowserLanguages(request)
            langs = browser_langs.getPreferredLanguages()
            try:
                return langs[0]
            except IndexError:
                return None
        else:
            return None

class UILanguage(BaseLanguageProvider):
    WEIGHT = 7
    def getLanguage(self):
        return get_request_language()

def get_default_language():
    # !+LANGUAGE(murithi, mar2011) need to integrate weights in registration
    # of utilities but overriding/new classes can also reorder negotiation
    # !+LANGUAGE(mr, apr-2011) what is the relation of this with:
    #   a) capi.default_language ?
    #   b) self.request.get("language") ?
    default_language = None
    language_providers = getUtilitiesFor(ILanguageProvider)
    provider_list = [(p[0], p[1]) for p in language_providers]
    sorted_providers = sorted(provider_list, key=lambda p: p[1].WEIGHT)
    for name, provider in sorted_providers:
        _language = provider()
        log.debug("Looking for language in %s found %s", name, _language)
        if _language and (_language in capi.zope_i18n_allowed_languages):
            default_language = _language
            log.debug("Got default language as %s from provider %s",
                        _language, name)
            break
    return default_language
    
def get_base_direction():
    request = get_request()
    ui_lang = request.getCookies().get("I18N_LANGUAGE")
    if ui_lang is not None:
        language = ui_lang
    else:
        language = capi.default_language
    if language[:2] in capi.right_to_left_languages:
        return "rtl"
    else:
        return "ltr"
             
@register.utility(provides=ITextDirection)
class TextDirection(object):
    def get_text_direction(self):
        return get_base_direction()
