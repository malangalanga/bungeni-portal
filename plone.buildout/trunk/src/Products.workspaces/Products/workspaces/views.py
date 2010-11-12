from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class GroupWorkspacesView(BrowserView):  
       
    def group_workspace_listing(self):
    
        context = aq_inner(self.context)
        gtool = getToolByName(context, 'portal_groups')
        grouplist = gtool.searchGroups()
        groups = gtool.getGroupWorkspacesFolder()
        
        for group in grouplist:
            if group.has_key('plugin'):
                if group['groupid'].rsplit('.')[1] == 'parliament':
                    parentFolder = getattr(groups, group['groupid'])

        categorygroups = []
        for group in parentFolder.getFolderContents():
            groupcategory = group.getId.rsplit('.')[1]
            if groupcategory not in categorygroups and groupcategory != 'parliament':
                categorygroups.append(groupcategory)
                

        categories = {}
        for categorygroup in categorygroups:
            categories[categorygroup] = []
    
        for group in parentFolder.getFolderContents():
            groupcategory = group.getId.rsplit('.')[1]
            if not categories.has_key(groupcategory):
                continue
            categories[groupcategory].append(group)
    
        return [{'category':categorygroup, 'items':categories[categorygroup]} for categorygroup in categorygroups]                             
