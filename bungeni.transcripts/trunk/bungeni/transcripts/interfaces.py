from zope.interface import Interface
from zope import schema
from bungeni.ui.i18n import _

class ITranscriptForm(Interface):
        start_time = schema.TextLine(
            title=_(u"Start Time"),
            required=True)
        end_time = schema.TextLine(
            title=_(u"EndTime"),
            required=True)
        speech = schema.Text(title=u'Speech Text',
                   required=False,
                   )
        person = schema.TextLine(title=u'Person',
                   required=False,
                   )

class ITranscribable(Interface):
    '''Transcribable Marker Interface'''
    
class ITranscript(Interface):
    '''Transcript Marker Interface'''

class IChange(Interface):
    """ Marker for Change (log table) """
    
class IVersion( Interface ):
    """
    a version of an object is identical in attributes to the actual object, based
    on that object's domain schema
    """

class IBungeniTake(Interface):
    '''Take Marker Interface'''

class IBungeniAssignment(Interface):
    '''Assignment Marker Interface'''
    
class IBungeniTranscriptsSitting(Interface):
    pass
    
class IBungeniTranscript(Interface):
    pass
