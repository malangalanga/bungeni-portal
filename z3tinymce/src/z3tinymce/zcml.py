from zope.component.zcml import handler
from interfaces import IZ3TinyMCEConfig
from zope.interface import implements


class Z3TinyMCEConfig(object):

    implements(IZ3TinyMCEConfig)
    path = ""

    def __init__(self, path):
        self.path = path

    def getPath(self):
        return self.path


def registerZ3TinyMCEConfig(context, path, port, maxConnections):
    context.action(discriminator=('RegisterOpenOfficeConfig', path),
                   callable=handler,
                   args = ('registerUtility',
                           Z3TinyMCEConfig(path), 
                           Iz3TinyMCEConfig)
                   )
