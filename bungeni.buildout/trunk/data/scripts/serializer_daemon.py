# part of Bungeni Parliamentary Information System copyright(c) 2013 UN/DESA Africa i-Parliaments Action Plan 
# licensed under GNU GPLv3
#

"""Serializer Process - this serializes Bungeni objects to XML. Objects are published to the Queue,
and this script reads from the Queue and published Objects to xml 
Has to be executed using the Bungeni Python - this script also sets up the Queues for Bungeni
"""

import sys
import bungeni
import logging
import os

from zope.configuration import xmlconfig
from bungeni.core.serialize import serialization_notifications
from bungeni.core.interfaces import IMessageQueueConfig
from zope.component import getUtility
from bungeni.core.app import BungeniApp


# setup logging
logging.basicConfig(level=logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# load zcml configuration
# get script folder 
current_folder = os.path.dirname(os.path.realpath(__file__))
site_zcml_path = os.path.join(current_folder, "..","..","src","bungeni.main","bungeni","site.zcml")
zcml = open(site_zcml_path)
zcml_slug = zcml.read()
xmlconfig.string(zcml_slug)

# initalize the app 
app = BungeniApp()

# load workflows
from bungeni.core.workflows import adapters
adapters.register_generic_workflow_adapters()

# load descriptors
import bungeni.ui.workflow
# ensure register version views
import bungeni.ui.versions
# load and apply-back UI descriptor customizations
from bungeni.ui.descriptor import localization
localization.forms_localization_init()
import bungeni.feature.ui
bungeni.feature.ui.setup_customization_ui()
bungeni.feature.ui.apply_customization_ui()

# setup serialization threads
worker_threads = serialization_notifications()

# keep the process alive by blocking the process
# until threads have finished (or have been interrupted)
try:
    for thread in worker_threads:
      while thread.isAlive():
          thread.join(5)
except (KeyboardInterrupt, SystemExit):
    print "ctrl -c pressed ! will exit"
    raise SystemExit

print "Threads finished executing ! exiting in 3 seconds !!"

import time
time.sleep(3)

