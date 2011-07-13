from md5 import md5
from sqlalchemy.types import TypeDecorator, Binary, String, UnicodeText
from sqlalchemy.util import buffer
from zope.component import getUtility
from zope.i18nmessageid.message import Message


class FSBlob(TypeDecorator, Binary):
    """ Sqlalchemy's type to store
        blob data in IFSUtility and the
        file name in the database.
        Deriving also from Binary class, for
        ore.alchemist to be able to translate it
        to zope.schema's field.
    """

    impl = String

    @property
    def fs(self):
        from bungeni.core.interfaces import IFSUtility
        return getUtility(interface=IFSUtility)

    def bind_processor(self, dialect):
        def process(value):
            if value:
                fname = md5(value).hexdigest()
                self.fs.store(value, fname)
                return fname
        return process

    def result_processor(self, dialect, coltype=None):
        def process(value):
            if not value:
                return None
            return buffer(self.fs.get(value) or '')
        return process

    def copy(self):
        return FSBlob()

class I18nAwareUnicodeText(TypeDecorator):
    
    impl = UnicodeText
    
    def process_bind_param(self, value, dialect):
        if isinstance(value, Message):
            value = unicode(value)
        return value

