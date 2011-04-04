#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bungeni - http://www.bungeni.org/
# Parliamentary and Legislative Information System
# Copyright (C) 2010 UN/DESA - http://www.un.org/esa/desa/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

'''Utilities to translate content

$Id$
'''
from copy import copy

from zope import component
from zope.security.proxy import removeSecurityProxy

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.security.management import getInteraction
from zope.publisher.interfaces import IRequest

from zope.publisher.browser import BrowserLanguages

from sqlalchemy import orm, sql

from plone.i18n.locales.interfaces import ILanguageAvailability

# !+CAPI(mr, feb-2011) the python used to execute this should have previously 
# set up os.environ["zope_i18n_allowed_languages",
# the value of which is parliament-specific and set in:
#   bungeni_custom.zope_i18n_allowed_languages
# Similar for: bungeni_custom.zope_i18n_compile_mo_files
# See zope.i18n.config for how these values are consumed.
# 
#from zope.i18n.config import ALLOWED_LANGUAGES
from bungeni.utils.capi import capi
ALLOWED_LANGUAGES = capi.zope_i18n_allowed_languages

from bungeni.alchemist import Session
from bungeni.core.interfaces import IVersionable
from bungeni.models.interfaces import IVersion, ITranslatable
from bungeni.models import domain
from bungeni.core.i18n import _
from bungeni.ui.utils import common


class BrowserFormLanguages(BrowserLanguages):

    def getPreferredLanguages(self):
        langs = super(BrowserFormLanguages, self).getPreferredLanguages()
        # use same cookie as linguaplone 
        form_lang = self.request.getCookies().get("I18N_LANGUAGE")
        if form_lang is not None:
            langs.insert(0, form_lang)
        return langs


class LanguageVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        languages = get_all_languages()
        items = [(l, languages[l].get('name', l)) for l in languages]
        items.sort(key=lambda language: language[1])
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

language_vocabulary_factory = LanguageVocabulary()


class CurrentLanguageVocabulary(LanguageVocabulary):
    def __call__(self, context):
        language = get_language(context)
        languages = get_all_languages(filter=[language])
        items = [(l, languages[l].get('name', l)) for l in languages]
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)


def get_language_by_name(name):
    return dict(get_all_languages())[name]

def get_default_language():
    return "en"

def get_language(translatable):
    return translatable.language

def get_all_languages(filter=None):
    """Build a list of all languages.

    To-do: the result of this method should be cached indefinitely.
    """
    availability = component.getUtility(ILanguageAvailability)
    _languages = availability.getLanguages(combined=True)
    if filter is None:
        filter = ALLOWED_LANGUAGES
    # TypeError if filter is not iterable
    return dict([ (name, _languages[name]) for name in filter ])

def get_request_language():
    return common.get_request().locale.getLocaleID() # !+ get_browser_language()


def get_translation_for(context, lang):
    """Get the translation for context in language lang
    NOTE: context may NOT be None
    """
    assert ITranslatable.providedBy(context), "%s %s" % (lang, context)
    trusted = removeSecurityProxy(context)
    class_name = trusted.__class__.__name__
    mapper = orm.object_mapper(trusted)
    pk = getattr(trusted, mapper.primary_key[0].name)
    session = Session()
    query = session.query(domain.ObjectTranslation).filter(
        sql.and_(
            domain.ObjectTranslation.object_type == class_name,
            domain.ObjectTranslation.object_id == pk,
            domain.ObjectTranslation.lang == lang
        )
    )
    return query.all()

def translate_obj(context, lang=None):
    """Translate an ITranslatable content object (context, that may NOT be None)
    into the specified language or that defined in the request
    -> copy of the object translated into language of the request
    """
    if lang is None:
        lang = get_request_language()
    trusted = removeSecurityProxy(context)
    translation = get_translation_for(trusted, lang)
    obj = copy(trusted)
    for field_translation in translation:
        setattr(obj, field_translation.field_name, 
            field_translation.field_text)
    return obj

'''
def translate_attr(obj, pk, attr_name, lang=None):
    """Translate a single object attribute, an optimization on translate_obj().
        
        !+TRANSLATE_ATTR(mr, sep-2010) as it turnes out (at least for a simple
        object e.g. ministry) this is slower than using translate_obj(obj).
    """
    if lang is None:
        lang = get_request_language()
    session = Session()
    query = session.query(domain.ObjectTranslation).filter(
        sql.and_(
            domain.ObjectTranslation.object_type == obj.__class__.__name__,
            domain.ObjectTranslation.object_id == pk,
            domain.ObjectTranslation.field_name == attr_name,
            domain.ObjectTranslation.lang == lang
        )
    )
    from sqlalchemy.orm.exc import NoResultFound
    try:
        return query.one().field_text
    except (NoResultFound,):
        return getattr(obj, attr_name)
'''

def get_available_translations(context):
    """ returns a dictionary of all
    available translations (key) and the object_id
    of the object (value)"""
    trusted = removeSecurityProxy(context)
    
    class_name = trusted.__class__.__name__
    try:
        mapper = orm.object_mapper(trusted)
        pk = getattr(trusted, mapper.primary_key[0].name)
        
        session = Session()
        query = session.query(domain.ObjectTranslation).filter(
            sql.and_(
                domain.ObjectTranslation.object_id == pk,
                domain.ObjectTranslation.object_type == class_name)
                ).distinct().values('lang','object_id')
            
        return dict(query)
    except:
        return {}

def is_translation(context):
    return IVersion.providedBy(context) and \
           context.status in (u"draft_translation",)
                      
