import logging

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from zExceptions import Forbidden
from itertools import chain

from zope.interface import Interface
from zope.component import adapts, getAdapter, getMultiAdapter, getUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from ZTUtils import make_query

from plone.protect import CheckAuthenticator
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from plone.app.controlpanel import usergroups

class GroupDetailsControlPanel(usergroups.UsersGroupsControlPanelView):

    def __call__(self):
        context = aq_inner(self.context)
        glist = getToolByName(self, 'acl_users').searchGroups()
         
        self.gtool = getToolByName(context, 'portal_groups')
        self.gdtool = getToolByName(context, 'portal_groupdata')
        self.regtool = getToolByName(context, 'portal_registration')
        self.groupname = getattr(self.request, 'groupname', None)
        self.grouproles = self.request.set('grouproles', [])
        self.group = self.gtool.getGroupById(self.groupname)
        self.grouptitle = self.groupname
        
        if self.group is not None:
            glist = [item for item in glist if item["groupid"] == self.group.id]
            if len(glist) == 1:
                self.grouptitle = glist[0]["title"]
            else:         
                self.grouptitle = self.group.getGroupTitleOrName()

        self.request.set('grouproles', self.group.getRoles() if self.group else [])

        submitted = self.request.form.get('form.submitted', False)
        if submitted:
            CheckAuthenticator(self.request)

            msg = _(u'No changes made.')
            self.group = None

            title = self.request.form.get('title', None)
            description = self.request.form.get('description', None)
            addname = self.request.form.get('addname', None)

            if addname:
                if not self.regtool.isMemberIdAllowed(addname):
                    msg = _(u'The group name you entered is not valid.')
                    IStatusMessage(self.request).add(msg, 'error')
                    return self.index()

                success = self.gtool.addGroup(addname, (), (), title=title,
                                              description=description,
                                              REQUEST=self.request)
                if not success:
                    msg = _(u'Could not add group ${name}, perhaps a user or group with '
                            u'this name already exists.', mapping={u'name' : addname})
                    IStatusMessage(self.request).add(msg, 'error')
                    return self.index()

                self.group = self.gtool.getGroupById(addname)
                msg = _(u'Group ${name} has been added.',
                        mapping={u'name' : addname})

            elif self.groupname:
                self.gtool.editGroup(self.groupname, roles=None, groups=None,
                                     title=title, description=description,
                                     REQUEST=context.REQUEST)
                self.group = self.gtool.getGroupById(self.groupname)
                msg = _(u'Changes saved.')

            else:
                msg = _(u'Group name required.')

            processed = {}
            for id, property in self.gdtool.propertyItems():
                processed[id] = self.request.get(id, None)

            if self.group:
                # for what reason ever, the very first group created does not exist
                self.group.setGroupProperties(processed)

            IStatusMessage(self.request).add(msg, type=self.group and 'info' or 'error')
            if self.group and not self.groupname:
                target_url = '%s/%s' % (self.context.absolute_url(), '@@usergroup-groupprefs')
                self.request.response.redirect(target_url)
                return ''

        return self.index()


class GroupsOverviewControlPanel(usergroups.UsersGroupsControlPanelView): 

    def __call__(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll', None) is not None
        self.searchString = not findAll and form.get('searchstring', '') or ''
        self.searchResults = []
        self.newSearch = False

        if search or findAll:
            self.newSearch = True

        if submitted:
            if form.get('form.button.Modify', None) is not None:
                self.manageGroup([group[len('group_'):] for group in self.request.keys() if group.startswith('group_')],
                                 form.get('delete', []))

        # Only search for all ('') if the many_users flag is not set.
        if not(self.many_groups) or bool(self.searchString):
            self.searchResults = self.doSearch(self.searchString)

        return self.index()
        
    def doSearch(self, searchString):
        """ Search for a group by id or title"""
        acl = getToolByName(self, 'acl_users')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        # First, search for inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_groups = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')
        allInheritedRoles = {}
        for group_info in inheritance_enabled_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)
            if not group_info['title']:
                group_info['title'] = group.getProperty('title', group_info['title'])
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                # getRolesForPrincipal can return None
                roles = rolemaker.getRolesForPrincipal(group) or ()
                allAssignedRoles.extend(roles)
            allInheritedRoles[groupId] = allAssignedRoles

        # Now, search for all roles explicitly assigned to each group.
        # We push this in the request so that IRoles plugins don't provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_groups = searchView.merge(chain(*[searchView.searchGroups(**{field: searchString}) for field in ['id', 'title']]), 'id')

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at all (None).
        results = []
        for group_info in explicit_groups:
            groupId = group_info['id']
            group = acl.getGroupById(groupId)
            if not group_info['title']:
                group_info['title'] = group.getProperty('title', group_info['title'])

            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                # getRolesForPrincipal can return None
                roles = rolemaker.getRolesForPrincipal(group) or ()
                explicitlyAssignedRoles.extend(roles)

            roleList = {}
            for role in self.portal_roles:
                canAssign = group.canAssignRole(role)
                if role == 'Manager' and not self.is_zope_manager:
                    canAssign = False
                roleList[role]={'canAssign': canAssign,
                                'explicit': role in explicitlyAssignedRoles,
                                'inherited': role in allInheritedRoles[groupId] }

            canDelete = group.canDelete()
            if roleList['Manager']['explicit'] or roleList['Manager']['inherited']:
                if not self.is_zope_manager:
                    canDelete = False

            group_info['roles'] = roleList
            group_info['can_delete'] = canDelete
            results.append(group_info)
        # Sort the groups by title
        sortedResults = searchView.sort(results, 'title')

        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        return sortedResults  
        
    def manageGroup(self, groups=[], delete=[]):
        CheckAuthenticator(self.request)
        context = aq_inner(self.context)

        groupstool=context.portal_groups
        utils = getToolByName(context, 'plone_utils')
        groupstool = getToolByName(context, 'portal_groups')

        message = _(u'No changes made.')

        for group in groups:
            roles=[r for r in self.request.form['group_' + group] if r]
            group_obj = groupstool.getGroupById(group)
            current_roles = group_obj.getRoles()
            if not self.is_zope_manager:
                # don't allow adding or removing the Manager role
                if ('Manager' in roles) != ('Manager' in current_roles):
                    raise Forbidden

            groupstool.editGroup(group, roles=roles, groups=())
            message = _(u'Changes saved.')

        if delete:
            for group_id in delete:
                group = groupstool.getGroupById(group_id)
                if 'Manager' in group.getRoles() and not self.is_zope_manager:
                    raise Forbidden

            groupstool.removeGroups(delete)
            message=_(u'Group(s) deleted.')

        utils.addPortalMessage(message)    
        
class UserMembershipControlPanel(usergroups.UsersGroupsControlPanelView):

    def update(self):
        self.userid = getattr(self.request, 'userid')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.member = self.mtool.getMemberById(self.userid)

        form = self.request.form

        self.searchResults = []
        self.searchString = ''
        self.newSearch = False

        if form.get('form.submitted', False):
            delete = form.get('delete', [])
            if delete:
                for groupname in delete:
                    self.gtool.removePrincipalFromGroup(self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

            add = form.get('add', [])
            if add:
                for groupname in add:
                    group = self.gtool.getGroupById(groupname)
                    if 'Manager' in group.getRoles() and not self.is_zope_manager:
                        raise Forbidden

                    self.gtool.addPrincipalToGroup(self.userid, groupname, self.request)
                self.context.plone_utils.addPortalMessage(_(u'Changes made.'))

        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll', None) is not None and not self.many_groups
        self.searchString = not findAll and form.get('searchstring', '') or ''

        if findAll or not self.many_groups or self.searchString != '':
            self.searchResults = self.getPotentialGroups(self.searchString)

        if search or findAll:
            self.newSearch = True

        self.groups = self.getGroups()

    def __call__(self):
        self.update()
        return self.index()

    def getGroups(self):
        groupResults = [self.gtool.getGroupById(m) for m in self.gtool.getGroupsForPrincipal(self.member)]
        groupResults.sort(key=lambda x: x is not None and normalizeString(x.getGroupTitleOrName()))
        return filter(None, groupResults)

    def getPotentialGroups(self, searchString):
        ignoredGroups = [x.id for x in self.getGroups() if x is not None]
        return self.membershipSearch(searchString, searchUsers=False, ignore=ignoredGroups)             
         
