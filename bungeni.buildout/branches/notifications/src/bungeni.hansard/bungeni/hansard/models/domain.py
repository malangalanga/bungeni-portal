from zope import interface, location, component
from bungeni.alchemist import Session
from alchemist.traversal.managed import one2many
from zope.location.interfaces import ILocation
import sqlalchemy.sql.expression as sql
from bungeni.models.domain import ItemLog, ItemVersions, Entity, GroupSitting, \
                                    ParliamentaryItem, Group, GroupMembership
from bungeni.hansard import interfaces
class Hansard(object):
    interface.implements(interfaces.IHansard)
    """
    The hansard report of a sitting
    It is made up of all the speechs of a sitting proceeding
    """   
    #speeches = one2many("speech", 
    #    "hansard.models.domain.SpeechContainer", "speech_id")
    

class HansardItem(ParliamentaryItem):
    """
    An item in the hansard ie. Parliamentary Item or Speech
    """

class HansardParliamentaryItem(HansardItem):
    """
    Parliamentary item discussed in a sitting
    """
    
    versions = one2many(
        "versions",
        "hansard.models.domain.HansardParliamentaryItemVersionContainer",
        "content_id")    
        
HansardParliamentaryItemChange = \
              ItemLog.makeLogFactory("HansardParliamentaryItemChange")
HansardParliamentaryItemVersion = \
              ItemVersions.makeVersionFactory("HansardParliamentaryItemVersion")
        
class Speech(HansardItem):
    """
    A single speech made in a plenary or committee sitting
    """
    
    versions = one2many(
        "versions",
        "hansard.models.domain.SpeechVersionContainer",
        "content_id")    
        
SpeechChange = ItemLog.makeLogFactory( "SpeechChange")
SpeechVersion = ItemVersions.makeVersionFactory("SpeechVersion")


class Take( Entity ):    
    """
    A Take - A unit of the parliamentary proceeding that is assigned to 
    a staff member for transcription or review
    """

class Assignment( Entity ):    
    """
    Contains the IDs of staff members assigned to work on a sitting
    """
class HansardMediaPaths( Entity ):
    """
    Media files of a sitting
    """


