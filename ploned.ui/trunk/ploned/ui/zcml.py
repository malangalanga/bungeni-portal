import os

from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import CheckerPublic, NamesChecker
from zope.component.zcml import handler
from zope.browserresource.metadirectives import IResourceDirectoryDirective
from zope.configuration.fields import GlobalInterface, Tokens

import skindirectory

allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault', 'layers',
                 'request', '__call__')

class ISkinDirectoryDirective( IResourceDirectoryDirective ):
    
    layers = Tokens(
        title=u"A list of layers",
        description=u"""
        This should be in order of lookup. Usually one of the layers
        has the same name as the skin, and the last layer should be
        'default', unless you want to completely override all views.
        """,
        required=False,
        value_type=GlobalInterface()
        )

def skinDirectory(_context, name, directory, layer=IDefaultBrowserLayer,
                      layers=(),
                      permission='zope.Public'):
    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names + ('__getitem__', 'get'),
                           permission)

    if not os.path.isdir(directory):
        raise ConfigurationError(
            "Directory %s does not exist" % directory
            )

    factory = skindirectory.SkinDirectoryFactory(directory, checker, name, layers)
    
    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter',
                factory, (layer,), Interface, name, _context.info),
        )
