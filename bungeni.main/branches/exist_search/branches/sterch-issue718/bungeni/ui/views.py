from bungeni.alchemist import Session
from bungeni.models import CurrentlyEditingDocument
from bungeni.models.utils import get_db_user_id
from datetime import datetime, timedelta
from zope.publisher.browser import BrowserView

from bungeni.core.serialize import obj2dict, serialize
import traceback
from zope.security.checker import getCheckerForInstancesOf
from bungeni.ui.utils.common import get_request_context_roles
from bungeni.utils.capi import capi
import os
from zope.security.proxy import removeSecurityProxy
from zipfile import ZipFile
from zope.securitypolicy.interfaces import IPrincipalRoleMap

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def setupStorageDirectory(part_target="xml_db"):
    # we start in buildout/src/bungeni.core/bungeni/core
    # we end in buildout/parts/index
    # TODO: this is probably going to break with package restucturing
    store_dir = __file__
    x = 0
    while x < 5:
        x += 1
        store_dir = os.path.split(store_dir)[0]
    store_dir = os.path.join(store_dir, 'parts', part_target)
    if os.path.exists(store_dir):
        assert os.path.isdir(store_dir)
    else:
        os.mkdir(store_dir)
    
    return store_dir

class Info(BrowserView):

    def __call__(self):
        try:
            context = removeSecurityProxy(self.context)
            
            map = IPrincipalRoleMap(context)
            print list(map.getPrincipalsAndRoles())
            files = []
            path = os.path.join(setupStorageDirectory(), self.context.type)
            if not os.path.exists(path):
                os.makedirs(path)
            file_path = os.path.join(path,context.__name__)
            files.append(file_path+'.xml') 
            with open(file_path+'.xml','w') as file:
                file.write(serialize(obj2dict(context,1,parent=None,include=['event','versions'],exclude=[])))
            if len(context.attached_files) > 0:
                for attachment in context.attached_files:
                    attachment_path = os.path.join(path, attachment.file_name)
                    files.append(attachment_path)
                    with open(os.path.join(path, attachment.file_name), 'wb') as file:
                         file.write(attachment.file_data)
                zip = ZipFile(file_path+'.zip', 'w')
                for file in files:
                    zip.write(file, os.path.split(file)[-1])
                    os.remove(file)
                zip.close()
                
                    
            return 'Done!'
        except:
            traceback.print_exception(*sys.exc_info())
            
        

class StoreNowEditView(BrowserView):
    """View that is periodically called
    with ajax requests to store the document
    id that the user is being currently
    editing"""

    def __call__(self):
        session = Session()

        # Current logged in user id
        user_id = get_db_user_id(self.context)

        # Looking if there is appropriate object to store
        # currently editing document data
        currently_editing_document = session.query(CurrentlyEditingDocument)\
                                            .filter(CurrentlyEditingDocument.user_id == user_id)\
                                            .first()

        # If not creating one for the current user
        if not currently_editing_document:
            currently_editing_document = CurrentlyEditingDocument()
            currently_editing_document.user_id = user_id
            session.add(currently_editing_document)

        # Assigning current document id
        document_id = self.context.parliamentary_item_id
        currently_editing_document.currently_editing_id = document_id

        # And the current date and time
        current_datetime = datetime.now()
        ago_datetime = current_datetime - timedelta(seconds=20)
        currently_editing_document.editing_date = current_datetime


        # Fetching amount of users that are being editing the document
        # taking into account that last time the ajax request was sent
        # no longer than 20 seconds ago
        count = session.query(CurrentlyEditingDocument)\
                       .filter(CurrentlyEditingDocument.currently_editing_id == document_id)\
                       .filter(CurrentlyEditingDocument.user_id != user_id)\
                       .filter(CurrentlyEditingDocument.editing_date.between(ago_datetime, current_datetime))\
                       .count()

        # Returning the amount, excluding current document editing
        return str(count)
