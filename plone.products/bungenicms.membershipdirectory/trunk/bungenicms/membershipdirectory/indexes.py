from plone.indexer import indexer

from bungenicms.membershipdirectory.interfaces import IMemberProfile

@indexer(IMemberProfile)
def member_full_names(obj):
    """
    Provide custom sorting title.

    This is used by various folder functions of Plone.
    This can differ from actual Title.
    """

    # Remember to handle None value if the object has not been edited yet
    surname = obj.Title() or ""
    other_names = obj.getOther_names() or ""
    
    return surname + " " + other_names
