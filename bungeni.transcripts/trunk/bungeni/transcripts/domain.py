import md5, random, string

from zope import interface, location, component
from ore.alchemist import model, Session
from alchemist.traversal.managed import one2many
from zope.location.interfaces import ILocation
import sqlalchemy.sql.expression as sql
from bungeni.models.domain import ItemLog, ItemVersions, Entity, GroupSitting, ParliamentaryItem
import logging
import interfaces

logger = logging.getLogger('bungeni.transcripts')


class Sitting( GroupSitting ):
    """ A Sitting """
    interface.implements( interfaces.IBungeniTranscriptsSitting  )
    
    transcripts2 = one2many("transcripts2", "bungeni.transcripts.domain.TranscriptContainer", "sitting_id")
    
    
class Transcript(ParliamentaryItem):
    """
    A Transcript
    """
    #interface.implements( interfaces.IAgendaItem )
    #interface.implements( bmi.IBungeniContent, interfaces.IBungeniTranscript  )
    
    versions = one2many(
        "versions",
        "bungeni.transcripts.domain.TranscriptVersionContainer",
        "content_id")    
TranscriptChange = ItemLog.makeLogFactory( "TranscriptChange")
TranscriptVersion = ItemVersions.makeVersionFactory("TranscriptVersion")


class Take( Entity ):    
    """
    A Take
    """
    interface.implements( interfaces.IBungeniTake  ) 

class Assignment( Entity ):    
    """
    A Take
    """
    interface.implements( interfaces.IBungeniAssignment ) 
