from zope import interface
from zope.configuration import fields

class IZ3TinyMCESchema(interface.Interface):
    path = fields.Path(
        title=u"Path to TinyMCE config file",
        description=u"Full path to Javascript file that contains TinyMCE config",
        required=True
        )
