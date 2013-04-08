"""
Repository utilities
"""
import re

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.i18n.locales.countries import countries

def slugify(st):
    return re.sub("[^\w\ ]+","", st).replace(" ","-").lower()


@apply
def country_vocabulary():
    terms = []
    country_listing = countries.getCountryListing()
    s_country_listing = sorted(country_listing, key=lambda c:c[0])
    for value,title in s_country_listing:
        terms.append(SimpleTerm(value=value, token=value, title=title))
    return SimpleVocabulary(terms)
