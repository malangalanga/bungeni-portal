from AccessControl import allow_module
from Acquisition import aq_inner
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.ATContentTypes.lib import constraintypes
from zope.app.component.hooks import getSite

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import nobody
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from Products.PlonePAS.utils import decleanId
from Products.ATContentTypes.lib import constraintypes
from Products.Five.utilities.marker import mark
from bungenicms.workspaces.interfaces import IMemberSpace, IGroupSpace

from bungenicms.workspaces.config import MEMBER_SPACE_CONTENT, GROUP_SPACE_CONTENT
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bungenicms.workspaces')


def doSearch(acl_tool, groupId):
    """ Search for a group by id or title"""
    rolemakers = acl_tool.plugins.listPlugins(IRolesPlugin)
    group = acl_tool.getGroupById(groupId)
    allAssignedRoles = []
    for rolemaker_id, rolemaker in rolemakers:
        allAssignedRoles.extend(rolemaker.getRolesForPrincipal(group))
    return allAssignedRoles

def create_space(parent, object_id, object_name, object_status, owner_id, owner, contenttype):  
    parent.invokeFactory(contenttype, id=object_id)
    space = getattr(parent, object_id)
    space.setTitle(object_name)
    space.manage_setLocalRoles(owner_id, ["Owner",])
    space.reindexObjectSecurity()
    space.content_status_modify(workflow_action=object_status)
    space.reindexObject
    
def create_content(parent, content, owner, content_status):
    for content_type in content:
        parent.invokeFactory(content_type["type"],id=content_type["id"])
        content = getattr(parent, content_type["id"])
        content.setTitle(content_type["title"])
        content.changeOwnership(owner)         
        content.content_status_modify(workflow_action=content_status)
        content.setConstrainTypesMode(constraintypes.ENABLED) 
        content.setLocallyAllowedTypes(content_type["addable_types"])
        content.setImmediatelyAddableTypes(content_type["addable_types"])
        content.reindexObject        

def initializeAreas(pm_tool, acl_tool, request, member_folder_id=None):
    """
    Creates custom content in the member's folder.
    Create group spaces and content for those groups.
    
    1. Create private space for the user.
    2. Create public space for user if they are a member of parliament.
    3. Populate the public space with initial custom content.
    4. Create group home folder for any groups (except a parliament) this user is a member of.
        4.1 Create a private space for the group home folder.
        4.2 Create a public space for the group home folder
        4.3 Populate the groups public space with initial custom content.
    """
    portal = getSite()
    sm = getSecurityManager()

    tmp_user = BaseUnrestrictedUser(sm.getUser().getId(),'', ['Manager'],'')
    newSecurityManager(None, tmp_user)    
    acl_tool = getToolByName(portal, 'acl_users')
    
    if "groups" in portal.objectIds():
        groups_space = portal["groups"]
    if member_folder_id:
        member = pm_tool.getMemberById(decleanId(member_folder_id))
    else:
        member = pm_tool.getAuthenticatedMember()
    member_id = member.getId()
    folder = pm_tool.getHomeFolder(member_id)
           
    #All members get a private workspace area. 
    create_space(folder, "private_space", _(u"Private Space"), "private", member_id, member, "PrivateFolder")
        
    member_groupIds = member.getGroupIds()
    for member_groupId in member_groupIds:
        group_membership_roles = doSearch(acl_tool, member_groupId)
        if "bungeni.MP" in group_membership_roles:
            create_space(folder, "web_space", _(u"Web Space"), "publish", member_id, member, "PublicFolder")
            parent_space = getattr(folder, "web_space")
            mark(parent_space, IMemberSpace)    
            create_content(parent_space, MEMBER_SPACE_CONTENT, member, "publish")


    groups_space = portal["groups"]

    for member_groupId in member_groupIds:
        group_membership_roles = doSearch(acl_tool, member_groupId)
        #if group home folder does not exist
        #it is cheaper to check if the group home folder already exists, then exit if it does
        for bungeni_group in acl_tool.bungeni_groups.enumerateGroups():

            if (member_groupId == bungeni_group["id"]) and ("bungeni.MP" not in group_membership_roles) and (bungeni_group["id"]not in groups_space.objectIds()):
                group = acl_tool.bungeni_groups.getGroupById(bungeni_group["id"])                 
                create_space(groups_space, bungeni_group["id"],
                    bungeni_group["title"], "private", bungeni_group["id"], 
                    group, "Folder")
                parent_space = getattr(groups_space, bungeni_group["id"])               
                create_space(parent_space, "private_space", _u("Private Space"), 
                    "private", bungeni_group["id"], 
                    group, "PrivateFolder")                       
                create_space(parent_space, "web_space", _(u"Web Space"), 
                    "publish", bungeni_group["id"], 
                     group, "PublicFolder") 
                parent_space = getattr(parent_space, "web_space")
                mark(parent_space, IGroupSpace)  
                create_content(parent_space, GROUP_SPACE_CONTENT, group, "publish")
                
