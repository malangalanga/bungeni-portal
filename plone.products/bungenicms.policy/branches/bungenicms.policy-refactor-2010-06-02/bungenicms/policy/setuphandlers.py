import logging

from zope import component
from zope.securitypolicy.interfaces import IRole
from Products.PluggableAuthService.interfaces.plugins import *
from bungeni.plonepas.install import install as install_plonepas
from Products.CMFCore.utils import getToolByName

member_indexhtml="""\
member_search=context.restrictedTraverse('membership_view')
return member_search()
"""


def setup_members_folder(context):
    """Set up the membership folder at <root>/membership.
    This will act as a members folder.

    These are the steps:
    
    1.  Create a large plone folder in public home /membership (or
    whatever you wish to call it)

    2.  ( If there is no large plone folder in drop down go to add
    large plone folder)

    3.  Then goto root and then bring your new /membership/ folder from
    public home to Plone root at aq_parent. The Membership folder has to
    be at the root, not public_home.

    4.  Goto portal membership properties at
    /aq_parent/portal_membership/manage_mapRoles
    Turn on member area creation

    5.  Set Member type to Large Plone folder if that is what you
    want.

    6.  Set Members folder to desired url e.g. /membership or /artists

    7.  If desired cut and paste members from old Members folder and
    place them in new folder.

    8.  If you wish the new Membership folder can be excluded from
    navigation bar.

    9. Create a default page for the Membership folder.
    """
    
    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()

    for name in ('news', 'events'):
        if name in portal.objectIds():
            portal[name].setExcludeFromNav(True)
            portal[name].update()

    if 'Members' in portal.objectIds():
        portal.manage_delObjects(ids=['Members'])

    if 'membership' in portal.objectIds():
        return logging.warn("Membership.")

    # create members folder (Large Plone Folder)
    pt = portal['portal_types']
    old_global_allow = pt['Large Plone Folder'].global_allow
    pt['Large Plone Folder'].global_allow = True
    members = portal[
        portal.invokeFactory(              
            "Large Plone Folder",
            id="membership")]
    pt['Large Plone Folder'].global_allow = old_global_allow
    
    # set default properties
    members.setTitle("membership")
    members.setDescription("membership")
    members._getWorkflowTool().doActionFor(members, 'publish' '')
    members.setExcludeFromNav(True)    
    members.reindexObject()

    # add index_html to Members area
    if 'index_html' not in members.objectIds():
        addPy = members.manage_addProduct['PythonScripts'].manage_addPythonScript
        addPy('index_html')
        index_html = getattr(members, 'index_html')
        index_html.write(member_indexhtml)
        index_html.ZPythonScript_setTitle('member listing')    

    # set members folder
    pm = portal['portal_membership']
    pm.memberareaCreationFlag = 1
    pm.setMembersFolderById('membership')


def setup_application_folders(context):
    
    """For each of the Bungeni top level menu-items we set up top-level folders that match the global routing table:

    application    mount-point
    ----------------------------------------------
    business           /business
    members            /members
    archive            /archive
    calendar           /calendar
    ----------------------------------------------

    Thereafter we create second-level folders for any applications that will be accessed at this level:
    
    application    mount-point
    ----------------------------------------------
    Dspace         /archive/dspace
    ----------------------------------------------
    """

    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()

    items = (
        ('business', u'business', u'business'),
        ('members', u'members', u'members of parliament'),
        ('archive', u'archive', u'archive'),
        ('calendar', u'calendar', u'calendar'))

    for name, title, description in items:
        if name not in portal.objectIds():
            obj = portal[portal.invokeFactory("Folder", id=name)]
            obj.setTitle(title)
            obj.setDescription(description)
            if name == 'calendar':
                obj.setExcludeFromNav(True)
            obj.reindexObject()
            wftool = getToolByName(portal, 'portal_workflow')
            if wftool.getInfoFor(obj, 'review_state') != 'published':
                wftool.doActionFor(obj, 'publish')
            


def setup_who_authentication(context):
    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()
    pas = portal.acl_users
    if getattr(pas, 'who', None) is not None:
        return
    
    pas.manage_addProduct['whoopass'].manage_addWhoPlugin('who')

    plugins = pas.plugins
    plugins.activatePlugin(IExtractionPlugin, 'who')
    plugins.activatePlugin(IAuthenticationPlugin, 'who')
    plugins.activatePlugin(IGroupsPlugin, 'who')
    plugins.activatePlugin(IPropertiesPlugin, 'who')
    plugins.activatePlugin(IRolesPlugin, 'who')

def setup_plonepas(context):
    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()
    return install_plonepas(portal)

def setup_z2_roles(context):
    if context.readDataFile('marker.txt') is None:
        return    
    portal = context.getSite()
    roles = list(portal.__ac_roles__)
    for name, role in component.getUtilitiesFor(IRole):
        if name not in roles:
            roles.append(name)
    roles.sort()
    portal.__ac_roles__ = tuple(roles)


def update_authenticated_users_group(context):
    if context.readDataFile('marker.txt') is None:
        return
    portal = context.getSite()
    groups_tool = portal.portal_groups
    group = groups_tool.getGroupById('AuthenticatedUsers')
    if 'Member' and 'bungeni.Anybody' and 'bungeni.Everybody' not in group.getRoles():
        roles = group.getRoles() + ['Member', 'bungeni.Anybody', 'bungeni.Everybody']
        groups_tool.editGroup(group.id, roles=roles, groups=())
        
    
def setup_group_workspaces(context):
    """Turn on workspace creation.
       Set Workspace container id to 'committees'
       Set group workspaces container type to folder
       Set group workspaces
       Create the group folder
       Turn off portal navigation for the groups folder.
    """

    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()
    if 'groups' not in portal.objectIds():
        gtool = getToolByName(portal, 'portal_groups')
        gtool.groupWorkspacesCreationFlag = 1
        gtool.setGroupWorkspacesFolder('groups', 'Groups')
        gtool.setGroupWorkspaceContainerType('Folder')
        gtool.setGroupWorkspaceType('Folder')
            
        # create groups folder (Folder)

        groups = portal[
            portal.invokeFactory(
                "Folder",
                id="groups")]

        # set default properties
        groups.setTitle("Groups")
        groups.setDescription("Group workspaces container.")
        groups._getWorkflowTool().doActionFor(groups, 'publish' '')
        groups.setExcludeFromNav(True)
        groups.update()
