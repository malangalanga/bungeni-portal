from zope.interface import Interface
import zope.schema as schema
from bungeni.ui.i18n import _

class ISearchResults(Interface):
    """Marker interface for results layer
    """
    pass

doc_type = schema.Choice(title=_("document type"),
    values=("*", "Bill", "Question", "AgendaItem", "Motion", 
        "TabledDocument", "Committee", "PoliticalGroup"),
    default="*",
    required=False
)

search_group = schema.Choice(title=_("group type"),
    values=("*", "document", "group", "membership"),
    default="*",
    required=False
)


class ISearchRequest(Interface):
    """Schema definition for search request parameters
    """
    search = schema.TextLine(title=_("search text"), required=False)
    type = schema.List(title=_("document types"),
        value_type=doc_type,
        required=False
    )
    group = schema.List(title=_("document groups"),
        value_type=search_group,
        required=False
    )
    limit = schema.Choice(title=_("items per page"),
        values=(10, 20, 50, 100),
        default=10,
        required=False
    )
    
    #status
    #offset
    #role (captured auto)
