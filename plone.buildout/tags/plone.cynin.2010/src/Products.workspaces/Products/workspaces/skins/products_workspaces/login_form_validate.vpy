## Script (Python) "validate_login_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validate login
##

# create member and group workspaces in the context of the root container.

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
import logging
logger = logging.getLogger("Products.workspaces.login_form_validate")

#create member and group Workspaces
group_tool = getToolByName(context, "portal_groups")
wftool = getToolByName(context, "portal_workflow")
parentGroup = group_tool.getGroupWorkspacesFolder()
grouplist = group_tool.searchGroups()
rootcontainer = getattr(context, "home")
pm = getToolByName(context, "portal_membership")
user_name = pm.getAuthenticatedMember().getId()
grouplist = group_tool.searchGroups()
spaces = [["private_folder", "Private folder", "retract"],
          ["web_pages", "Web pages", "publishanonymous"]]


def create_space(parent, object_id, object_name, object_status, owner_id):
    parent.invokeFactory("ContentSpace", id=object_id)
    space = getattr(parent, object_id)
    space.setTitle(object_name)
    
    #assign user all roles for this space.
    portal_wrkflow_tool = getToolByName(space, "portal_workflow")    
    owner_access = ("Owner", "Editor", "Contributor", "Reader")
    space.manage_setLocalRoles(owner_id, list(owner_access))
    portal_wrkflow_tool.updateRoleMappings()
    
    #apply the spaces workflow
    placeful_wrkflow_tool = getToolByName(space, "portal_placeful_workflow")
    space.manage_addProduct["CMFPlacefulWorkflow"].manage_addWorkflowPolicyConfig()
    config = placeful_wrkflow_tool.getWorkflowPolicyConfig(space)
    config.setPolicyIn(policy="ubify_spaces_workflow")
    config.setPolicyBelow(policy="ubify_spaces_content_workflow")
    space.content_status_modify(workflow_action=object_status)
    space.reindexObject()          
    

def create_workspace(space_id, space_title):
    if space_id not in rootcontainer.objectIds():
        logger.info("Creating  - %s Content Space" % (space_id))
        create_space(rootcontainer, space_id, space_title, "retract", space_id)
        user_space = getattr(rootcontainer, space_id)
        for space in spaces:
            logger.info("Creating %s for user - %s" % (space[0], space_id))
            create_space(user_space, space[0], space[1], space[2], space_id)

#Create members individual workspaces
create_workspace(user_name, user_name)

#Create group workspaces
group_types_not_to_create = ['parliament', 'ministry', 'government']
[create_workspace(
    group['groupid'], group['title']
    ) for group in grouplist if group.has_key('plugin') and (
     group['groupid'].rsplit('.')[1] not in group_types_not_to_create)]



request = context.REQUEST
js_enabled = request.get("js_enabled",0) # is javascript enabled?
js_enabled = js_enabled=="1" or js_enabled==1
cookies_enabled = request.get("cookies_enabled",0) # are cookies enabled?
cookies_enabled = cookies_enabled=='1' or cookies_enabled==1

if js_enabled and not cookies_enabled:
    context.plone_utils.addPortalMessage(_(
        u'You must enable cookies before you can log in.'), 'error')
    state.set(status='enable_cookies')
    return state

mt=context.portal_membership
if mt.isAnonymousUser():
    # javascript is enabled - we can diagnose the failure
    if js_enabled:
        # using cookie authentication?
        auth = getattr(context, 'cookie_authentication', None)
        if auth:
            user_name = request.get('login_name', None)
            password_empty = request.get('pwd_empty', None)=='1'
            ac_name = auth.name_cookie
            ac_password = auth.pw_cookie

            if not user_name:
                # no user name
                state.setError(ac_name, _(u'Please enter your login name.'),
                               'login_name_required')
            if password_empty:
                state.setError(ac_password, _(u'Please enter your password.'),
                               'password_required')
            login_name = context.portal_properties.site_properties.getProperty(
                'verify_login_name', 0)
            if user_name and login_name:
                # XXX mixing up username and loginname here
                if mt.getMemberById(user_name) is None:
                    state.setError(ac_name, _(u'Login name not found.'),
                                   'login_name_not_found')
                elif not password_empty:
                    state.setError(ac_password, _(u'Password incorrect.'),
                                   'password_incorrect')
        context.plone_utils.addPortalMessage(_(
            u'Login failed. Both login name and password are case sensitive, \
            check that caps lock is not enabled.'), 'error')
        state.set(status='failure')
    else: # no javascript - do low tech login failure
        context.plone_utils.addPortalMessage(_(
            u'Login failed. Both login name and password are case sensitive, \
            check that caps lock is not enabled.'), 'error')
        state.set(status='failure_page')

return state
