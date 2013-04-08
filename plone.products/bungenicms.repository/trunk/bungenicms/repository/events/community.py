from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.CMFPlone.utils import getToolByName

from bungenicms.repository.interfaces import IRepositoryCommunity

import logging

CONTRIBUTOR_ROLES = ['Contributor']

class CreateCommunityAuthStructure(object):
    
    inteface = IRepositoryCommunity
    
    @property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups', None) 

    def __init__(self, object, event):
                
        self.context = event.object

        if IObjectInitializedEvent.providedBy(event):
            # create group
            logging.info('Creating user group for community %s',
            self.context.title)
            group_name = self.get_group_name(self.context)
            if self.portal_groups is not None:
                group_exists = self.portal_groups.getGroupById(group_name)
                if group_exists is None:
                    self.portal_groups.addGroup(group_name)
                self.context.manage_setLocalRoles(group_name,
                                                    CONTRIBUTOR_ROLES)
                self.context.reindexObjectSecurity()
                logging.info('Updated sharing settings for community %s',
                              self.context.title)
            else:
                logging.error('Unable to access portal groups tool')
                
        else:
            #initialization event did not fire
            pass

    def get_group_name(self, context):
        return "%s Members" %(self.context.title)
        
        
