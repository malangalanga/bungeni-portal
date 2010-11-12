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

# create group workspaces in the context of a parent (parliament).

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

group_tool = getToolByName(context, 'portal_groups')
wftool = getToolByName(context, 'portal_workflow')
parentGroup = group_tool.getGroupWorkspacesFolder()
grouplist = group_tool.searchGroups()



def createGroupArea(groupid, grouptitle, parentFolder):
    """Use the log-in as a hook to create group workspaces.
    The groups are created from the bungeni application and
    not through the traditional Groups tab.
    """

    if groupid not in context.groups.objectIds():

        group = context.portal_groups.getGroupById(groupid)
        members = [group.id for group in group.getGroupMembers()]
        if groupid not in parentFolder.objectIds():
            parentFolder.invokeFactory('Folder', groupid, title=grouptitle)
            obj = getattr(parentFolder, groupid, None)
            obj.setTitle("%s workspace" %grouptitle)
            obj.setDescription("Container for objects shared by this group")
            obj.manage_setLocalRoles(groupid, ['Owner'])
            wftool.doActionFor(obj, 'publish')
            obj.update
            obj.reindexObject()

            #create space for annotatable/amendable documents.
            folder_id = "documents_for_comment"
            folder_title = "Documents for comment"
            obj.invokeFactory('Folder', id=folder_id)
            newfolder = getattr(obj, folder_id, None)
            newfolder.setTitle(folder_title)
            wftool.doActionFor(newfolder, 'publish')
            newfolder.update
            newfolder.reindexObject()

        
for group in grouplist:
    if group.has_key('plugin'):
        if group['groupid'].rsplit('.')[1] == 'parliament':
            createGroupArea(group['groupid'], group['title'], parentGroup)
            parentFolder = getattr(parentGroup, group['groupid'])

[createGroupArea(group['groupid'], group['title'], parentFolder ) for group in grouplist if group.has_key('plugin') and group['groupid'].rsplit('.')[1] != 'parliament']



request = context.REQUEST
js_enabled = request.get('js_enabled',0) # is javascript enabled?
js_enabled = js_enabled=='1' or js_enabled==1
cookies_enabled = request.get('cookies_enabled',0) # are cookies enabled?
cookies_enabled = cookies_enabled=='1' or cookies_enabled==1

if js_enabled and not cookies_enabled:
    context.plone_utils.addPortalMessage(_(u'You must enable cookies before you can log in.'), 'error')
    state.set(status='enable_cookies')
    return state

mt=context.portal_membership
if mt.isAnonymousUser():
    if js_enabled: # javascript is enabled - we can diagnose the failure
        auth = getattr(context, 'cookie_authentication', None) # using cookie authentication?
        if auth:
            user_name = request.get('login_name', None)
            password_empty = request.get('pwd_empty', None)=='1'
            ac_name = auth.name_cookie
            ac_password = auth.pw_cookie

            if not user_name:
                # no user name
                state.setError(ac_name, _(u'Please enter your login name.'), 'login_name_required')
            if password_empty:
                state.setError(ac_password, _(u'Please enter your password.'), 'password_required')
            verify_login_name = context.portal_properties.site_properties.getProperty('verify_login_name', 0)
            if user_name and verify_login_name:
                # XXX mixing up username and loginname here
                if mt.getMemberById(user_name) is None:
                    state.setError(ac_name, _(u'Login name not found.'), 'login_name_not_found')
                elif not password_empty:
                    state.setError(ac_password, _(u'Password incorrect.'), 'password_incorrect')
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
        state.set(status='failure')
    else: # no javascript - do low tech login failure
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
        state.set(status='failure_page')

return state
