from bungeni.ui.descriptor import ParliamentaryItemDescriptor 
from bungeni.ui.i18n import _
from copy import deepcopy
class TranscriptDescriptor(ParliamentaryItemDescriptor): 
    display_name =_(u"Transcripts")
    container_name =_(u"Transcripts")
    fields = deepcopy(ParliamentaryItemDescriptor.fields )
