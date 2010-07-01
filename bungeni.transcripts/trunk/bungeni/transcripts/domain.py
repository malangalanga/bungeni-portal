import md5, random, string

from zope import interface, location, component
from ore.alchemist import model, Session
from alchemist.traversal.managed import one2many
from zope.location.interfaces import ILocation
import sqlalchemy.sql.expression as sql

from bungeni.models.domain import ItemLog
from bungeni.models.domain import ItemVersions
import logging
import interfaces

logger = logging.getLogger('bungeni.transcripts')



class Entity( object ):

    interface.implements( location.ILocation )

    __name__ = None
    __parent__ = None
    
    def __init__( self, **kw ):
        try:
            domain_schema = model.queryModelInterface( self.__class__ )
            known_names = [k for k,d in domain_schema.namesAndDescriptions(1)]
        except:
            known_names = None

        for k,v in kw.items():
            if known_names is None or k in known_names:
                setattr( self, k, v)
            else:
                logger.warn(
                    "Invalid attribute on %s %s" % (
                        self.__class__.__name__, k))


class Sitting( Entity ):
    """ A Sitting """
    interface.implements( interfaces.IBungeniTranscriptsSitting  )
    
    transcripts = one2many("transcripts", "bungeni.transcripts.domain.TranscriptContainer", "id")
    
    
class Transcript( Entity ):    
    """
    A Transcript
    """
    #interface.implements( interfaces.IAgendaItem )
    interface.implements( interfaces.IBungeniTranscript  )
    
    versions = one2many(
        "versions",
        "bungeni.transcripts.domain.TranscriptVersionContainer",
        "content_id")    
TranscriptChange = ItemLog.makeLogFactory( "TranscriptChange")
TranscriptVersion = ItemVersions.makeVersionFactory("TranscriptVersion")
