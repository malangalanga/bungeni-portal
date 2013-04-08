from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

import datetime

#log = __import__("logging").getLogger("bungenicms.repository.setup")

def YearVocabulary(context): 

    items = []
    
    # Get a datetime object
    now = datetime.datetime.now()
    currentYear = now.year
    startYear = 1950
    
    items.append( (str(0), str(0), "--") )
    for eachYear in range(startYear, (currentYear + 5), 1):
        items.append( (str(eachYear), str(eachYear), str(eachYear)) )
    
    terms = [ SimpleTerm(value=pair[0], token=pair[1], title=pair[2]) for pair in items ]  

    return SimpleVocabulary(terms)
    
    
def MonthVocabulary(context):
    
    items = []
    
    # Get a datetime object
    now = datetime.datetime.now()
    currentYear = now.year
    
    items.append( (str(0), "--") )
    
    for i in range(1, 13, 1):
        items.append( (str(i), datetime.date(currentYear, i, 1).strftime('%B')) )
    
    terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]  

    return SimpleVocabulary(terms)


def DayVocabulary(context):

    items = []
    
    items.append( (str(0), "--") )
    
    for i in range(1, 32, 1):
        items.append( ( str(i), str(i) ) )
    
    terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]  

    return SimpleVocabulary(terms)
