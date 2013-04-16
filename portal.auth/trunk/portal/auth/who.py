"""
``repoze.who`` authenticator plugins against a relational database
"""
log = __import__("logging").getLogger("portal.auth.who")
from datetime import datetime
from paste.httpheaders import REQUEST_METHOD
from paste.httpheaders import PATH_INFO
from paste.httpheaders import CONTENT_TYPE
from paste.httpheaders import AUTHORIZATION
from paste.httpexceptions import HTTPUnauthorized
from zope import interface
from zope.app.security.principalregistry import principalRegistry
from zope.app.security.interfaces import PrincipalLookupError
from repoze.who.interfaces import (
    IAuthenticator, IMetadataProvider, IRequestClassifier, IIdentifier,
    IChallenger)
from bungeni.alchemist import Session
from sqlalchemy.exc import UnboundExecutionError
import sqlalchemy as rdb
from sqlalchemy.orm import eagerload, lazyload

from bungeni.models import domain, delegation

# !+MODEL_MAPPING(mn, oct-2011) import bungeni.models.orm is needed to ensure 
# that mappings of domain classes to schema tables is executed.
from bungeni.models import orm


def get_user(login_id):
    session = Session()
    try:
        db_user = session.query(domain.User).filter(
            domain.User.login == login_id).one()
    except rdb.orm.exc.NoResultFound:
        log.warn("No user with login id, %s exists" % login_id)
        return None
    except rdb.orm.exc.MultipleResultsFound:
        #Should never happen as login column is unique
        log.error("Multiple users found with same login id, %s" % login_id)
        raise
    else:
        return db_user


def get_user_groups(login_id):
    """Get group for users:
    a) the groups defined by his user_group_memberships
    b) the users who have him assigned as a delegation
    c) the groups of the delegation user.
    """
    def get_groups(user_id):
        principal_ids = []
        session = Session()
        query = session.query(domain.GroupMembership).filter(rdb.and_(
                    domain.GroupMembership.user_id == user_id,
                    domain.GroupMembership.active_p == True)
            ).options(eagerload("group"), lazyload("user"))
        for membership in query:
            principal_ids.append(membership.group.principal_name)
        return principal_ids
    groups = set()
    user = get_user(login_id)  # user may be None
    if user:
        groups.add(login_id)
        user_id = user.user_id
        for elem in get_groups(user_id):
            groups.add(elem)
        for user in delegation.get_user_delegations(user):
            for elem in get_groups(user.user_id):
                groups.add(elem)
            groups.add(user.login)
    return groups


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
        user = get_user(identity['login'])
        if user and user.checkPassword(identity['password']):
            return identity['login']

    def add_metadata(self, environ, identity):
        userid = identity.get('repoze.who.userid')
        user = get_user(userid)
        groups = None
        if user is not None:
            groups = tuple(self.get_groups(userid))
            try:
                session = Session()
            except UnboundExecutionError, e:
                log.warn(e)
            admin_user = session.query(domain.AdminUser).get(user.user_id)
            if admin_user:
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


def bungeni_request_classifier(environ):
    """ Returns one of the classifiers 'api', 'xmlpost', or 'browser',
    depending on the imperative logic below"""
    if PATH_INFO(environ).startswith("/api"):
        return 'api'
    request_method = REQUEST_METHOD(environ)
    if request_method == 'POST':
        if CONTENT_TYPE(environ) == 'text/xml':
            return 'xmlpost'
    return 'browser'
interface.directlyProvides(bungeni_request_classifier, IRequestClassifier)


class OAuthIdentifierPlugin(object):
    interface.implements(IIdentifier)

    def identify(self, environ):
        authorization = AUTHORIZATION(environ)
        tokens = authorization.split(" ")
        if len(tokens) != 2:
            return None
        if tokens[0] != "Bearer":
            return None
        return {"access_token": tokens[1]}

    def forget(self, environ, identity):
        return None

    def remember(self, environ, identity):
        return None


class OAuthChallengerPlugin(object):

    interface.implements(IChallenger)

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        return HTTPUnauthorized()


class OAuthAuthenticatorPlugin(AlchemistWhoPlugin):
    """OAuth identifier, authenticator"""
    interface.implements(IAuthenticator, IMetadataProvider)

    def authenticate(self, environ, identity):
        if not identity:
            return None
        if not "access_token" in identity:
            return None
        session = Session()
        try:
            access_token = session.query(domain.OAuthAccessToken).filter(
                rdb.and_(
                    domain.OAuthAccessToken.access_token == identity["access_token"], 
                    domain.OAuthAccessToken.expiry > datetime.now()
                )).one()
        except rdb.orm.exc.NoResultFound:
            return None
        except rdb.orm.exc.MultipleResultsFound:
            # One in a gazillion chance that same access token is generated twice
            log.error("Multiple records for same access token.")
            return None
        if access_token.authorization_token.authorization.active == False:
            return None
        return access_token.authorization_token.authorization.user.login










