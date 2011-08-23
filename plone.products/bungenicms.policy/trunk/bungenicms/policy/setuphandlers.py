import logging

from zope import component
from zope.securitypolicy.interfaces import IRole
from Products.PluggableAuthService.interfaces.plugins import *
from bungenicms.plonepas.install import install as install_plonepas
from Products.CMFCore.utils import getToolByName
import bungeni_custom as bc

logger = logging.getLogger("Plone")

def setup_site_languages(context):
    """ Setup site langauge settings
    """
    portal = context.getSite()
    ltool = portal.portal_languages
                   
    defaultLanguage = bc.default_language
    supportedLanguages = list(bc.zope_i18n_allowed_languages.split())
    ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                      setUseCombinedLanguageCodes=True,
                                      setCookieN=True, setRequestN=True)
    logger.info("Site languages enabled.")                                        

def turn_on_member_workspaces(context):
    """Set up the membership folder at <root>/membership.
    This will act as a members folder. Set Member Area Creation On
    """
    portal = context.getSite()
    
    if "Members" in portal.objectIds():
        portal.manage_delObjects(ids=["Members"])

    if "membership" not in portal.objectIds():  
        # create members container folder and set default properties
        pt = portal["portal_types"]
        members = portal[portal.invokeFactory("Folder",id="membership")]
        members.setTitle("membership")
        members.setDescription("Member workspaces container.")
        members._getWorkflowTool().doActionFor(members, "publish" "")
        members.setExcludeFromNav(True)    
        members.reindexObject()           
    
        # set members folder
        pm = portal['portal_membership']
        pm.memberareaCreationFlag = 1
        pm.setMembersFolderById('membership') 
        logger.info("Members container created.")          


def setup_who_authentication(context):
    if context.readDataFile("marker.txt") is None:
        return

    portal = context.getSite()
    pas = portal.acl_users
    if getattr(pas, "who", None) is not None:
        return
    
    pas.manage_addProduct["whoopass"].manage_addWhoPlugin("who")

    plugins = pas.plugins
    plugins.activatePlugin(IExtractionPlugin, "who")
    plugins.activatePlugin(IAuthenticationPlugin, "who")
    plugins.activatePlugin(IGroupsPlugin, "who")
    plugins.activatePlugin(IPropertiesPlugin, "who")
    plugins.activatePlugin(IRolesPlugin, "who")

def setup_plonepas(context):
    if context.readDataFile("marker.txt") is None:
        return

    portal = context.getSite()
    return install_plonepas(portal)

def setup_z2_roles(context):
    if context.readDataFile("marker.txt") is None:
        return    
    portal = context.getSite()
    roles = list(portal.__ac_roles__)
    for name, role in component.getUtilitiesFor(IRole):
        if name not in roles:
            roles.append(name)
    roles.sort()
    portal.__ac_roles__ = tuple(roles)


def update_authenticated_users_group(context):
    if context.readDataFile("marker.txt") is None:
        return
    portal = context.getSite()
    groups_tool = portal.portal_groups
    group = groups_tool.getGroupById("AuthenticatedUsers")
    if "Member" and "bungeni.Anonymous" and "bungeni.Authenticated" not in \
        group.getRoles():
        roles = group.getRoles() + \
            ["Member", "bungeni.Anonymous", "bungeni.Authenticated"]
        groups_tool.setRolesForGroup(group.id, 
            ("Member","bungeni.Anonymous", "bungeni.Authenticated"))        
        
    
def setup_group_workspaces(context):
    """Create group workspaces parent folder.
    """
    if context.readDataFile("marker.txt") is None:
        return

    portal = context.getSite()
    if "groups" not in portal.objectIds():

        groups = portal[
            portal.invokeFactory("Folder",id="groups")]

        # set default properties
        groups.setTitle("groups")
        groups.setDescription("Group workspaces container.")
        groups._getWorkflowTool().doActionFor(groups, "publish" "")
        groups.setExcludeFromNav(True)
        groups.update()  
        logger.info("Groups container created.")   

def setup_folders(context):
    portal = context.getSite()
    for name in ("news", "events"):
        if name in portal.objectIds():
            portal[name].setExcludeFromNav(True)
            portal[name].update()
            logger.info("Hiding %s folder from the main navbar" % name)
