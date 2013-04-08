import urllib
import httplib2
import simplejson

from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable

from Products.PlonePAS.plugins.group import PloneGroup
from Products.PlonePAS.interfaces import group as IPloneGroups
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import (IGroupsPlugin,
                                                              IGroupEnumerationPlugin)
from utils import connection_url

manage_addBungeniGroupManagerForm = PageTemplateFile("zmi/group-plugin-add.pt",
                                        globals())

def manage_addBungeniGroupManager(self, id, db_utility, title="", REQUEST=None):
    """Add a GroupManager to a Pluggable Auth Service."""
    rm = GroupManager(id, db_utility, title)
    self._setObject( id, rm)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                "%s/manage_workspace"
                                "?manage_tabs_message="
                                "BungeniGroupManager+added."
                            % self.absolute_url())

class GroupManager(BasePlugin, Cacheable):

    meta_type = "Bungeni Group Manager"

    security = ClassSecurityInfo()

    
    def __init__(self, id, title=None):
        self.id = self.id = id
        self.title = title

    #
    # IGroupsPlugin implementation
    #
    
    def getGroupsForPrincipal(self, principal, request=None):
        """ principal -> ( group_1, ... group_N )

        o Return a sequence of group names to which the principal 
          (either a user or another group) belongs.

        o May assign groups based on values in the REQUEST object, if present
        """
        #XXX TODO: user delegations!, implement search for groups 
        # recursivly for this use case

        http_obj=httplib2.Http()
        query = "/++rest++brs/memberships?"
        params = urllib.urlencode({"principal_id": principal.getId()})
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        return simplejson.loads(content)
    
    #
    # IGroupsEnumeration implementation
    #

    def enumerateGroups( self, id=None
                       , exact_match=False
                       , sort_by=None
                       , max_results=None
                       , **kw
                       ):
        """ see IGroupEnumeration """
        http_obj=httplib2.Http()
        querys = "/++rest++brs/enumerategroups?"
        params = urllib.urlencode({"group_manager_id": self.id,
                                   "gid": id,
                                   "exact_match": exact_match,
                                   "sort_by": sort_by,
                                   "max_results": max_results})
        resp,content = http_obj.request(connection_url() + querys + params, "GET")
        return simplejson.loads(content)            
        

    ####################
    # IGroupManagement 
    ####################
    
    def addGroup(self, id, **kw):
        """
        Create a group with the supplied id, roles, and groups.
        return True if the operation suceeded
        """
        raise NotImplementedError

        
    def addPrincipalToGroup(self, principal_id, group_id):
        """
        Add a given principal to the group.
        return True on success
        """
        raise NotImplementedError("Add principals to groups not implemented.")


    def updateGroup(self, id, **kw):
        """
        Edit the given group. plugin specific
        return True on success
        """

        raise NotImplementedError("Group updates not implemented.")

    def setRolesForGroup(self, group_id, roles=()):
        """
        set roles for group
        return True on success
        """
        # why the heck is this even in the group api ? 
        #silly enfold developers.. tricks are for kids
        raise NotImplemented

    
    #   IDeleteCapability implementation
    def allowDeletePrincipal(self, principal_id):
        """True if this plugin can delete a certain group."""
        return False

        if self.getGroupById(principal_id):
            return True
        return False


    #   IGroupCapability implementation
    def allowGroupAdd(self, user_id, group_id):
        """True if this plugin will allow adding a certain user to a certain group."""
        return False

        present = self.enumerateGroups(id=group_id)
        
        # if we have a group, we can add users to it
        # slightly naive, but should be okay.
        if present: return True   
                                  
        return False

    def allowGroupRemove(self, user_id, group_id):
        """
        True if this plugin will allow removing a certain user
        from a certain group.
        """
        return False
        present = self._gid(group_id)
        
        # if we don't have a group, we can't do anything
        if not present: return False   
        
        groups = self.getGroupsForPrincipal(user_id)
        if group_id in groups: return True
        return False

    def removeGroup(self, group_id):
        """
        Remove the given group
        return True on success
        """
        return False
        # XXX also need to delete all memberships in the group,
        # just set group as inactive
        #gid = self._gid( group_id )
        #schema.groups.delete().where( schema.groups.c.group_id == gid ).execute()

    def removePrincipalFromGroup(self, principal_id, group_id):
        """
        remove the given principal from the group
        return True on success
        """
        raise NotImplementedError
        
    
    ###########################
    # IGroupIntrospection
    ###########################
    def _gid(self, name):
        http_obj=httplib2.Http()
        query = "/++rest++brs/groups?"
        params = urllib.urlencode({'name': name})
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        groups = simplejson.loads(content)
        if not groups:
            return
        return groups["principal_name"]
        

    def _uid(self, login):
        http_obj=httplib2.Http()
        query = "/++rest++brs/users?"
        params = urllib.urlencode({"login": login})
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        user = simplejson.loads(content)
        if user is None:
            return
        return user.user_id        
        

    def getGroupById(self, group_id):
        """
        Returns the portal_groupdata-ish object for a group
        corresponding to this id.
        """
        gid = self._gid( group_id )
        if not gid:
            return None
        return PloneGroup(gid).__of__( self )
        

    #################################
    # these interface methods are suspect for scalability.
    #################################

    def getGroups(self):
        """
        Returns an iteration of the available groups
        """
        http_obj=httplib2.Http()
        query = "/++rest++brs/groups"
        resp,content = http_obj.request(connection_url() + query, "GET")
        groups = simplejson.loads(content)
        return [PloneGroup(r).__of__(self) for r in groups]
        
    def getGroupIds(self):
        """
        Returns a list of the available groups
        """
        http_obj=httplib2.Http()
        query = "/++rest++brs/groups"
        resp,content = http_obj.request(connection_url() + query, "GET")
        groups = simplejson.loads(content)
        

    def getGroupMembers(self, group_id):
        """
        return the members of the given group
        """
        
        http_obj=httplib2.Http()
        query = "/++rest++brs/groupmembers?"
        params = urllib.urlencode({"group_id": group_id})
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        return simplejson.loads(content)


classImplements( GroupManager,
                 IGroupsPlugin,
                 IGroupEnumerationPlugin,
                 IPloneGroups.IGroupIntrospection,
                 IPloneGroups.IGroupManagement )
