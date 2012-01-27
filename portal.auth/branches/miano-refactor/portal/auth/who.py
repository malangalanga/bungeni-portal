"""
``repoze.who`` authenticator plugins against a relational database
"""
log = __import__("logging").getLogger("portal.auth.who")

from zope import interface
from zope.app.security.principalregistry import principalRegistry
from zope.app.security.interfaces import PrincipalLookupError

from repoze.who.interfaces import IAuthenticator
from repoze.who.interfaces import IMetadataProvider

#from bungeni.alchemist import Session
from ore.alchemist import Session
from bungeni.alchemist.interfaces import IDatabaseEngine
from sqlalchemy.sql import select
#from bungeni.models import domain, delegation
from bungeni.models import schema
import md5
from sqlalchemy import create_engine
from zope import component
from ore.alchemist.interfaces import IDatabaseEngine
# !+MODEL_MAPPING(mn, oct-2011) import bungeni.models.orm is needed to ensure 
# that mappings of domain classes to schema tables is executed.
#from bungeni.models import orm

def get_user_id(login_id):
    db_user_select = select([schema.users], schema.users.c.login == login_id)
    session = Session()
    result = session.connection().execute(db_user_select)
    if len(result) == 0:
        log.warn("No user with login id, %s exists" % login_id)
        return None
    elif len(result) > 1:
        # !+non_unique_login(mr, oct-2011) impossible, login column is UNIQUE!
        log.error("Multiple users found with same login id, %s" % login_id)
        return None
    else:
        return result.fetchone()[schema.users.c.login]

def get_user_delegations(user_id):
    """ get all delegations for a given user_id
    user_id = schema.users.c.user_id
    both delegator and delegee must be active
    """
    user_delegations_select = ([schema.user_delegations, schema.users], 
        and_(schema.user_delegations.c.delegation_id == user_id, 
              schema.user.c.active_p == 'A',
              schema.user_delegations.c.active_p == 'A'))
    session = Session()
    results = session.connection().execute(user_delegations_select)
    return [result[schema.users.c.login] for result in results]

def get_user_groups(login_id):
    """Get group for users:
    a) the groups defined by his user_group_memberships
    b) the users who have him assigned as a delegation
    c) the groups of the delegation user.
    """
    def get_groups(user_id):
        user_group_membserhip_select = select([schema.user_group_memberships, schema.groups],
            and_(schema.user_group_memberships.c.user_id == user_id,
                 schema.user_group_memberships.c.active_p == True,
                 schema.user_group_memberships.c.group_id == schema.groups.c.group_id
                 ))
        session = Session()
        results = session.connection().execute(user_group_membership_select)
        return [result[schema.groups.c.group_principal_id] for result in results]
    groups = set()
    user_id = get_user_id(login_id) # user may be None
    if user_id: 
        groups.add(login_id)
        for elem in get_groups(user_id):
            groups.add(elem)
        for user in get_user_delegations(user_id):
            for elem in get_groups(user.user_id):
                groups.add(elem)
    return groups

def encode(password, salt):
    return md5.md5(password + salt).hexdigest()

def checkPassword(user_id, password_attempt):
    attempt = encode(password_attempt, salt)
    user_select = select([schema.users], schema.users.c.user_id == user_id)
    result = con.execute(user_select)
    return attempt == result.fetchone()[schema.users.c.password]

class AlchemistWhoPlugin(object):
    interface.implements(IAuthenticator, IMetadataProvider)
    
    def get_groups(self, login_id):
        groups = get_user_groups(login_id)
        groups.add("zope.Authenticated")
        groups.add("zope.anybody")
        return groups

    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None
        user = get_user_id(identity['login'])
        if user and checkPassword(user, identity['password']):
            return identity['login']

    def add_metadata(self, environ, identity):
        login_id = identity.get('repoze.who.userid')
        user_id = get_user_id(login_id)
        groups = None
        if user_id is not None:
            groups = tuple(self.get_groups(user_id))
            admin_select = select([schema.admin_users], schema.users.c.user_id == user_id)
            session = Session()
            result = session.connection().execute(admin_select)
            if result.fetchone():
                groups = groups + ('zope.manager',)
            identity.update({
                'email': user.email,
                'title': u"%s, %s" % (user.last_name, user.first_name),
                'groups': groups,
                })


class GlobalAuthWhoPlugin(object):
    interface.implements(IAuthenticator, IMetadataProvider)

    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None

        principal = self.get_principal_by_login(identity['login'])
        if principal and principal.validate(identity['password']):
            return identity['login']

    def get_principal(self, id):
        try:
            return principalRegistry.getPrincipal(id)
        except PrincipalLookupError:
            pass
        except KeyError:
            pass

    def get_principal_by_login(self, login):
        try:
            return principalRegistry.getPrincipalByLogin(login)
        except PrincipalLookupError:
            pass
        except KeyError:
            pass

    def add_metadata(self, environ, identity):
        login = identity.get('repoze.who.userid')
        principal = self.get_principal_by_login(login)
        if principal is not None:
            identity.update({
                'title': principal.title,
                'groups': tuple(principal.groups) + (principal.id,),
                })
