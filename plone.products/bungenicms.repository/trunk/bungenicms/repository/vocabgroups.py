from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

log = __import__("logging").getLogger("bungenicms.repository.setup")

def GroupsVocabulary(context): 

    items = []
    acl_users = getToolByName(context, 'acl_users')

    items.append( (str(0), "--") )
    for group in acl_users.searchGroups():
        if (group["id"], group["title"]) not in items:
            items.append((group["id"], group["title"]))
            
    terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]

    return SimpleVocabulary(terms)
