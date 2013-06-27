from AccessControl import allow_module
from Acquisition import aq_inner
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.ATContentTypes.lib import constraintypes
from zope.app.component.hooks import getSite

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from Products.PlonePAS.utils import decleanId
from Products.ATContentTypes.lib import constraintypes
from Products.Five.utilities.marker import mark
from bungenicms.workspaces.interfaces import IMemberSpace, IGroupSpace

from bungenicms.workspaces.config import MEMBER_SPACE_CONTENT 
from bungenicms.workspaces.config import GROUP_SPACE_CONTENT
from bungenicms.workspaces.config import PUBLIC_FOLDER_ENTRY_NAME
from bungenicms.workspaces.config import PRIVATE_FOLDER_ENTRY_NAME
from bungenicms.workspaces.config import ROLES_FOR_WEB_SPACE

def doSearch(acl_tool, groupId):
    """ Search for a group by id or title"""
    rolemakers = acl_tool.plugins.listPlugins(IRolesPlugin)
    group = acl_tool.getGroupById(groupId)
    allAssignedRoles = []
    for rolemaker_id, rolemaker in rolemakers:
        allAssignedRoles.extend(rolemaker.getRolesForPrincipal(group))
    return allAssignedRoles

def create_space(parent, object_id, object_name, object_status, owner_id, owner,
                    contenttype):   
    portal = getSite()
    portal_types = getToolByName(portal, "portal_types")
    type_info = portal_types.getTypeInfo(contenttype)
    space = type_info._constructInstance(parent, object_id)
    space.setTitle(object_name)
    portal.plone_utils.changeOwnershipOf( space, portal.getOwner().getId(), 1 )
    space._setRoles(owner_id, ("Reader","Contributor","Editor", "Reviewer")) 
    space.reindexObjectSecurity()
    space.content_status_modify(workflow_action=object_status)
    space.reindexObject
    
def create_content(parent, content, owner, content_status):
    #Create custom content.
    for content_type in content:
        parent.invokeFactory(content_type["type"],id=content_type["id"])
        content = getattr(parent, content_type["id"])
        content.setTitle(content_type["title"])
        content.manage_setLocalRoles(owner.getId(), ["Contributor","Editor",]) 
        content.content_status_modify(workflow_action=content_status)
        content.setConstrainTypesMode(constraintypes.ENABLED) 
        content.setLocallyAllowedTypes(content_type["addable_types"])
        content.setImmediatelyAddableTypes(content_type["addable_types"])
        content.reindexObject        

def initializeAreas(pm_tool, acl_tool, request, member_folder_id=None):
    """
    Creates custom content in the member's home folder.
    Create group spaces and content for the member's groups.
    
    1. Create private space for the user.
    2. Create public space for user if they are a member of parliament.
    3. Populate the public space with custom content
    4. Create group home folder for any groups (except a parliament) this user 
        is a member of.
        4.1 Create a private space for the group home folder.
        4.2 Create a public space for the group home folder
        4.3 Populate the public space with custom content.
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
    mark(folder, IMemberSpace)


    #All members get a private workspace area.
    create_space(folder, "private_space", "Private Space", "private", member_id,
                    member, PRIVATE_FOLDER_ENTRY_NAME)
    member_groupIds = member.getGroupIds()
    for member_groupId in member_groupIds:
        group_membership_roles = doSearch(acl_tool, member_groupId)
        
        if bool(set(ROLES_FOR_WEB_SPACE) & set(group_membership_roles)):
            create_space(folder, "web_space", "Web Space", "publish", member_id,
                            member, PUBLIC_FOLDER_ENTRY_NAME)
            parent_space = getattr(folder, "web_space")
            mark(parent_space, IMemberSpace)    
            create_content(parent_space, MEMBER_SPACE_CONTENT, member,
                            "publish")


    groups_space = portal["groups"]

    for member_groupId in member_groupIds:
        group_membership_roles = doSearch(acl_tool, member_groupId)
        #if group home folder does not exist
        #it is cheaper to check if the folder exists, then exit if it does
        for bungeni_group in acl_tool.bungeni_groups.enumerateGroups():

            if ((member_groupId == bungeni_group["id"])
                and (not bool(set(ROLES_FOR_WEB_SPACE) & set(group_membership_roles)))
                and (bungeni_group["id"]not in groups_space.objectIds())):
                group = acl_tool.bungeni_groups.getGroupById(bungeni_group["id"])                 
                create_space(groups_space, bungeni_group["id"],
                    bungeni_group["title"], "private", bungeni_group["id"], 
                    group, "Folder")
                parent_space = getattr(groups_space, bungeni_group["id"]) 
                mark(parent_space, IGroupSpace)              
                create_space(parent_space, "private_space", "Private Space", 
                    "private", bungeni_group["id"], 
                    group, PRIVATE_FOLDER_ENTRY_NAME)                       
                create_space(parent_space, "web_space", "Web Space", 
                    "publish", bungeni_group["id"], 
                     group, PUBLIC_FOLDER_ENTRY_NAME) 
                parent_space = getattr(parent_space, "web_space")
                mark(parent_space, IGroupSpace)  
                create_content(parent_space, GROUP_SPACE_CONTENT, group,
                                "publish")
                
