#register skins directory
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl import allow_module
GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""   
