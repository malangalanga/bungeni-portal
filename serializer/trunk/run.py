import sys
import bungeni
import logging

from zope.configuration import xmlconfig
from bungeni.core.serialize import serialization_notifications
from bungeni.core.interfaces import IMessageQueueConfig
from zope.component import getUtility
from bungeni.core.app import BungeniApp

logging.basicConfig(level=logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

### Test by including all zcml imports from site.zcml ####

zcml_slug = """<configure
      	 xmlns="http://namespaces.zope.org/meta"
	 xmlns:i18n="http://namespaces.zope.org/i18n"
         xmlns:bungeni="http://namespaces.bungeni.org/zope"
         xmlns:db="http://namespaces.objectrealms.net/rdb"
         i18n_domain="bungeni"
       >
         <directive
      name="messagequeue"
      namespace="http://namespaces.bungeni.org/zope"
      schema="bungeni.core.interfaces.IMessageQueueConfigSchema"
      handler="bungeni.core.notifications.registerMessageQueueConfig"
      />
    <!-- Message queue settings -->
    <bungeni:messagequeue
      message_exchange="bungeni" 
      task_exchange="bungeni_notification_tasks"
      username="admin"
      password="admin"
    />


   <!-- App Security -->
    <include package="bungeni" file="security.zcml" />

    <!-- Application Configuration -->
    <include package="ploned.ui" file="meta.zcml" />



    <include package="bungeni.alchemist" file="meta.zcml" />
    <db:engine name="bungeni-db" 
        url="postgres://localhost/bungeni"
        echo="false"
    />


    <include package="bungeni.core" />
    <includeOverrides file="overrides.zcml" package="bungeni.core" />
</configure>
"""
# load zcml configuration
xmlconfig.string(zcml_slug)

# initalize the app 
app = BungeniApp()


#mq = getUtility(IMessageQueueConfig)
#print mq


# import schema metadata
import bungeni.models.schema.metadata
import bungeni.alchemist.security.metadata

# load workflow and register adapters
from bungeni.core.workflows import adapters
adapters.register_generic_workflow_adapters()

worker_threads = serialization_notifications()

for thread in worker_threads:
   try:
     thread.join()
   except (KeyboardInterrupt, SystemExit):
     raise SystemExit

print "Threads finished executing ! exiting in 3 seconds !!"

import time
time.sleep(3)

