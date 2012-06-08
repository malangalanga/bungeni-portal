import urllib
import httplib2
import simplejson
import random
import md5
import string

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Globals import InitializeClass

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserAdderPlugin
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PluggableAuthService.interfaces.plugins import IRoleAssignerPlugin
from Products.PluggableAuthService.interfaces.plugins import IRoleEnumerationPlugin

from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PlonePAS.interfaces.capabilities import IDeleteCapability
from Products.PlonePAS.interfaces.capabilities import IPasswordSetCapability
from Products.PlonePAS.interfaces.capabilities import IAssignRoleCapability

from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.permissions import SetOwnPassword

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from utils import connection_url

manage_addBungeniUserManagerForm = PageTemplateFile('zmi/user-plugin-add.pt', globals())

def manage_addBungeniUserManager(self, id, title='', REQUEST=None):
    """Add a BungeniUserManager to a Pluggable Auth Service."""
    um = UserManager(id, title )
    self._setObject(um.getId(), um)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'BungeiUserManager+added.'
                            % self.absolute_url())

def generate_salt( ):
    return ''.join( random.sample( string.letters, 12 ) )

def encrypt(word, salt):
    return md5.md5( word + salt).hexdigest()

def safeencode(v):
    if isinstance(v, unicode):
        return v.encode('utf-8')
    return v

class UserManager(BasePlugin):
    meta_type = 'Bungeni User Manager'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self.id = self.id = id
        self.title = title

    security.declarePrivate('invalidateCacheForChangedUser')
    def invalidateCacheForChangedUser(self, user_id):
        pass

    #
    # IUserManagement implementation
    #

    security.declarePrivate('doChangeUser')
    def doChangeUser(self, login, password, **kw):
        # userSetPassword in PlonePAS expects a RuntimeError when a plugin doesn't hold the user.
        try:
            self.updateUserPassword(login, login, password)
        except KeyError:
            raise RuntimeError, "User does not exist: %s"%login


    security.declarePrivate('doDeleteUser')
    def doDeleteUser(self, login):
        try:
            self.removeUser(login)
        except KeyError:
            return False
        return True
    
    #
    # IDeleteCapability implementation
    #

    def allowDeletePrincipal(self, id):
        return self._uid( id ) is not None


    #
    # IPasswordSetCapability implementation
    #
    def allowPasswordSet(self, id):
        return self._uid( id ) is not None

    #
    # IAuthenticationPlugin implementation
    #

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')
        if not login or not password: return None
        
        res = self._uid( login, auth=True )
        if not res: return None
        
        if encrypt( password, res['salt'] ) == res['password']:
            return login, login
        return None
        
    #
    # IUserEnumerationPlugin implementation
    #
    security.declarePrivate('enumerateUsers')
    def enumerateUsers(self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):
        """See IUserEnumerationPlugin.
        """
        if id is None:
            id = login

        http_obj=httplib2.Http()
        query = '/++rest++brs/enumerateusers?'
        params = urllib.urlencode({'user_manager_id': self.id,
                                   'id': id,
                                   'login': login,
                                   'exact_match': exact_match,
                                   'sort_by': sort_by,
                                   'max_results': max_results,
                                   'kw': kw})

        resp,content = http_obj.request(connection_url() + query + params, "GET")
        return simplejson.loads(content)          


    #
    # IUserAdderPlugin implementation
    #
    security.declarePrivate('doAddUser')
    def doAddUser(self, login, password):
        try:
            self.addUser(login, login, password)
        except KeyError:
            return False
        return True

    #
    # (notional)IZODBUserManager interface
    #
    security.declareProtected(ManageUsers, 'listUserIds')
    def listUserIds(self):
        http_obj=httplib2.Http()
        query = '/++rest++brs/users'
        resp,content = http_obj.request(connection_url() + query, "GET")
        users = simplejson.loads(content)
        return users

    security.declareProtected(ManageUsers, 'listUserInfo')
    def listUserInfo(self):
        http_obj=httplib2.Http()
        query = '/++rest++brs/users?'
        params = urllib.urlencode({'user_manager_id': self.id})        
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        users = simplejson.loads(content)
        return users
    

    security.declareProtected(ManageUsers, 'getUserInfo')
    def getUserInfo(self, user_id ):
        uid = self._uid( user_id )
        if not uid:
            return None
        return dict( id=user_id, login=user_id, pluginid=self.id )

    security.declareProtected(ManageUsers, 'getLoginForUserId')
    def getLoginForUserId(self, user_id):
        return user_id
    
    security.declarePrivate('addUser')
    def addUser(self, user_id, login_name, password): # raises keyerror, lookup error
        salt = generate_salt()
        e_pass = encrypt( password, salt )
        if self._uid( login_name ):
            raise KeyError("Duplicate User Id: %s"%user_id)
        h=httplib2.Http()
        query = '/++rest++brs/users'
        data = {"login": user_id,
                "salt": salt,
                "password": e_pass,
                "type": "user",
                "first_name": u"unknown",
                "last_name": u"unknown",
                "email": u"unknown"}
        params = urllib.urlencode(data)
        resp,content = h.request(connection_url()+ query, params, "POST")
        
    
    security.declarePrivate('removeUser')
    def removeUser(self, user_id): # raises keyerror
        uid = self._uid( user_id )
        if not uid:
            raise KeyError("Invalid User"%uid)
        # update user to show as inactive
        http_obj=httplib2.Http()
        query = '/++rest++brs/users'
        data = {"uid": uid}
        params = urllib.urlencode(data)
        resp,content = http_obj.request(connection_url()+ query, params, "DELETE")
        

    security.declarePrivate('updateUserPassword')
    def updateUserPassword(self, user_id, login_name, password): # raise keyerror, lookup error
        uid = self._uid( user_id )
        if uid is None:
            raise KeyError("Invalid User %s"%user_id )
        salt = generate_salt()
        e_pass = encrypt( password, salt )

        http_obj=httplib2.Http()
        query = '/++rest++brs/users'
        data = {"uid": uid,
                "salt": salt,
                "password": e_pass}
        params = urllib.urlencode(data)
        resp,content = http_obj.request(connection_url()+ query, params, "PUT") 


    # Allow users to change their own login name and password.
    #
    security.declareProtected(SetOwnPassword, 'getOwnUserInfo')
    def getOwnUserInfo(self):
        """Return current user's info."""
        user_id = getSecurityManager().getUser().getId()
        return self.getUserInfo(user_id)
    
    def _uid(self, login, auth=False):

        http_obj=httplib2.Http()
        query = '/++rest++brs/users?'
        data = {"auth": auth,
                "login": login}
        params = urllib.urlencode(data)
        resp,content = http_obj.request(connection_url()+ query + params, "GET")
        

    def _gid(self, name):
        http_obj=httplib2.Http()
        query = '/++rest++brs/groups?'
        params = urllib.urlencode({'name': name})
        resp,content = http_obj.request(connection_url() + query + params, "GET")
        groups = simplejson.loads(content)        
        if not groups:
            return
        return groups[0].group_principal_id

    def allowRoleAssign(self, prinicipal_id, role_id):
        if role_id.startswith('bungeni.'):
            return True

    """ Assign a role to an identified principal
    """

    def assignRolesToPrincipal(self, roles, principal_id, setting=True):
        if self._uid(principal_id) is None and self._gid(principal_id) is None:
            return

        if setting is True:
            # delete global mappings
            
            http_obj=httplib2.Http()
            query = '/++rest++brs/roles'
            data = {'principal_id': principal_id}
            params = urllib.urlencode(data)
            resp,content = http_obj.request(connection_url()+ query, params, "DELETE")               
            
            # update existing

            http_obj=httplib2.Http()
            query = '/++rest++brs/roles'
            data = {'principal_id': principal_id}
            params = urllib.urlencode(data)
            resp,content = http_obj.request(connection_url()+ query, params, "PUT")
            
        # insert new global mappings

            http_obj=httplib2.Http()
            query = '/++rest++brs/roles'
            data = {'roles': roles,
                    'principal_id': principal_id,
                    'setting': setting}            
            params = urllib.urlencode(data)
            resp,content = http_obj.request(connection_url()+ query, params, "POST")
            
        return True
    
    def doAssignRoleToPrincipal(self, principal_id, role ):

        """ Create a principal/role association in a Role Manager

        o Return a Boolean indicating whether the role was assigned or not
        """
        return self.assignRolesToPrincipal((role,), principal_id)

    def doRemoveRoleFromPrincipal(self, principal_id, role ):

        """ Remove a principal/role association from a Role Manager

        o Return a Boolean indicating whether the role was removed or not
        """

        return self.assignRolesToPrincipal((role,), principal_id, False)

    def getRolesForPrincipal(self, principal, request=None ):

        """ principal -> ( role_1, ... role_N )

        o Return a sequence of role names which the principal has.

        o May assign roles based on values in the REQUEST object, if present.
        """

        http_obj=httplib2.Http()
        query = '/++rest++brs/roles?'
        params = urllib.urlencode({'principal_id': principal.getId()})
        resp,content = http_obj.request(connection_url()+ query + params, "GET")
        if "bungeni.Owner" in content:
            roles = simplejson.loads(content)
            roles.append("Manager")
            return roles          
        else:
            return simplejson.loads(content)        





    """ Allow querying roles by ID, and searching for roles.
    """
    def enumerateRoles(self,
                        id=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):

        """ -> ( role_info_1, ... role_info_N )

        o Return mappings for roles matching the given criteria.

        o 'id' in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' may be treated by 
          the plugin as "contains" searches (more complicated searches 
          may be supported by some plugins using other keyword arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' (some plugins may support others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all roles satisfying the 
          criteria.

        o Minimal keys in the returned mappings:
        
          'id' -- (required) the role ID

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'properties_url' -- (optional) the URL to a page for updating the
                              role's properties.

          'members_url' -- (optional) the URL to a page for updating the
                           principals to whom the role is assigned.

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid critera.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """

        pluginid = self.getId()

        http_obj=httplib2.Http()
        query = '/++rest++brs/enumerateroles?'
        params = urllib.urlencode({'plugin_id': self.getId()})
        resp,content = http_obj.request(connection_url()+ query + params, "GET")

        return simplejson.loads(content)
            
classImplements( UserManager,
                 IAuthenticationPlugin,
                 IUserEnumerationPlugin,
                 IUserAdderPlugin,
                 IUserManagement,
                 IDeleteCapability,
                 IPasswordSetCapability,
                 IRolesPlugin,
                 IRoleAssignerPlugin,
                 IRoleEnumerationPlugin,
                 IAssignRoleCapability )

InitializeClass( UserManager )
