from zope.component.zcml import handler
from interfaces import IOpenOfficeConfig, IMessageQueueConfig
from zope.interface import implements


class OpenOfficeConfig(object):

    implements(IOpenOfficeConfig)
    path = ""
    port = None
    maxConnections = None
    
    def __init__(self, path, port, maxConnections):
        self.path = path
        self.port = port
        self.maxConnections = maxConnections
        
    def getPath(self):
        return self.path
    
    def getPort(self):
        return self.port
    
    def getMaxConnections(self):
        return self.maxConnections
        
def registerOpenOfficeConfig(context, path, port, maxConnections):

   context.action(discriminator=('RegisterOpenOfficeConfig', path, port, 
                                                                maxConnections),
                   callable=handler,
                   args = ('registerUtility', 
                            OpenOfficeConfig(path, port, maxConnections), 
                            IOpenOfficeConfig)
                   )

class MessageQueueConfig(object):

    implements(IMessageQueueConfig)
    '''exchange = ""
    username = ""
    password = ""
    host = ""
    port = None
    virtual_host = ""
    channel_max = None
    frame_max = None
    heartbeat = None'''
    
    def __init__(self, exchange, username, password, host, port, virtual_host,
                channel_max, frame_max, heartbeat):
        self.exchange = exchange
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.channel_max = channel_max
        self.frame_max = frame_max
        self.heartbeat = heartbeat
        
    def get_exchange(self):
        return self.exchange
        
    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_host(self):
        return self.host
        
    def get_port(self):
        return self.port
        
    def get_virtual_host(self):
        return self.virtual_host
        
    def get_channel_max(self):
        return self.channel_max
        
    def get_frame_max(self):
        return self.frame_max
        
    def get_heartbeat(self):
        return self.heartbeat

def registerMessageQueueConfig(context, exchange, username="", password="", host="", port=None, virtual_host="",
                channel_max=None, frame_max=None, heartbeat=None):
    context.action(discriminator=('RegisterMessageQueueConfig'),
                   callable=handler,
                   args=('registerUtility',
                            MessageQueueConfig(exchange, username, password, host, port, 
                            virtual_host, channel_max, frame_max, heartbeat),
                            IMessageQueueConfig)
                   )
