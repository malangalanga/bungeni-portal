import hashlib
import datetime
from zope import formlib
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserPage
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from bungeni.ui.i18n import _
from bungeni.ui import forms
from bungeni.ui.browser import BungeniBrowserView
from bungeni.capi import capi
from bungeni.models import domain
from bungeni.models.utils import get_db_user
from bungeni.alchemist import Session
from bungeni.ui.utils import url


class APIDefaultView(BungeniBrowserView):
    def __call__(self):
        return ""


class AddOauthApplication(forms.common.AddForm):

    def get_app_key(self, app_id, app_name):
        m = hashlib.sha256()
        m.update(app_id+app_name+capi.oauth_secret)
        return m.hexdigest()

    @formlib.form.action(_(u"Create Application"), name="create")
    def handle_create_application(self, action, data, validator="validateAdd"):
        oauth_app = domain.OauthApplication()
        oauth_app.application_identifier = data["application_identifier"]
        oauth_app.application_name = data["application_name"]
        oauth_app.application_key = self.get_app_key(
            oauth_app.application_identifier,
            oauth_app.application_name)
        session = Session()
        session.add(oauth_app)
        session.flush()
        notify(ObjectCreatedEvent(oauth_app))
        next_url = url.absoluteURL(self.__parent__, self.request)
        self.request.response.redirect(next_url)

    @formlib.form.action(_(u"Cancel"), name="cancel")
    def handle_cancel(self, action, data):
        next_url = url.absoluteURL(self.__parent__, self.request)
        self.request.response.redirect(next_url)


class OauthException(Exception):

    def __init__(self, redirect_uri, state=None):
        self.redirect_uri = redirect_uri
        self.state = state

    @property
    def error(self):
        raise NotImplemented

    @property
    def error_description(self):
        raise NotImplemented


class UnauthorizedClient(OauthException):
    @property
    def error(self):
        return "unauthorized_client"

    @property
    def error_description(self):
        return "The client is not authorized to request an authorization" \
               " code using this method."


class UnsupportedResponseType(OauthException):
    @property
    def error(self):
        return "unsupported_response_type"

    @property
    def error_description(self):
        return "The authorization server does not support obtaining an" \
               " authorization code using this method."


class AccessDenied(OauthException):
    @property
    def error(self):
        return "access_denied"

    @property
    def error_description(self):
        return "The resource owner or authorization server denied the" \
               " request."


class InvalidRequest(OauthException):
    @property
    def error(self):
        return "invalid_request"

    @property
    def error_description(self):
        return "The request is missing a required parameter, includes an" \
               " invalid parameter value, includes a parameter more than" \
               " once, or is otherwise malformed."


class AuthorizeForm(formlib.form.FormBase):
    def __init__(self, context, request,  parameters):
        self.parameters = parameters
        super(AuthorizeForm, self).__init__()

    def generate_authorization_code(user_id, application_identifier):
        m = hashlib.sha256()
        m.update("%d" % (user_id) + capi.oauth_secret + application_identifier)
        return m.hexdigest()

    @formlib.form.action(_(u"Authorize application"), name="authorize")
    def handle_authorize_app(self, action, data):
        session = Session()
        oauth_authorization = domain.OauthAuthorization()
        oauth_authorization.user_id = get_db_user().user_id
        app = session.query(domain.OauthApplication
            ).filter(domain.OauthApplication.application_identifier ==
                 self.request.form.get("client_id")
            ).one()
        oauth_authorization.application_id = app.application_id
        oauth_authorization.auth_code = generate_authorization_code(
            oauth_authorization.user_id, oauth_authorization.application_id)
        oauth_authorization.expiry = datetime.now() + datetime.timedelta(
            seconds=capi.oauth_auth_expiry_time)
        session.add(oauth_authorization)
        self.request.response.redirect()
    
    @formlib.form.action(_(u"Cancel"), name="cancel")
    def handle_cancel(self, action, data):
        next_url = url.absoluteURL(self.__parent__, self.request)
        self.request.response.redirect(next_url)



class APIOauthAuthorization(BrowserPage):

    def process_parameters(self):
        session = Session()
        parameters = {}

        parameters["state"] = self.request.form.get("state", None)

        if self.request.form.get("redirect_uri", None):
            parameters["redirect_uri"] = self.request.form.get("redirect_uri")
        else:
            # rfc6749 4.1.1 states that the redirect_uri is optional.
            # use a default one if one is not supplied
            parameters["redirect_uri"] = "https://www.bungeni.org/oauth"

        if self.request.form.get("response_type", None):
            if self.request.form.get("response_type") != "code":
                raise UnsupportedResponseType(
                    parameters["redirect_uri"], parameters["state"])
            else:
                parameters["response_type"] = "code"
        else:
            raise InvalidRequest(
                parameters["redirect_uri"], parameters["state"])

        if self.request.form.get("client_id", None):
            try:
                parameters["client_id"] = session.query(domain.OauthApplication
                    ).filter(domain.OauthApplication.application_identifier ==
                             self.request.form.get("client_id")
                    ).one()
            except:
                raise UnauthorizedClient(
                    parameters["redirect_uri"], parameters["state"])
        else:
            raise InvalidRequest(
                parameters["redirect_uri"], parameters["state"])

        return parameters

    

    def __call__(self):
        try:
            parameters = self.process_parameters()
        except OauthException as e:
            next_url = "%s?error=%s&error_description=%s" % (e.redirect_uri,
                e.error, e.error_description)
            if e.state:
                next_url = next_url + "&state=%s" % (e.state)
            self.request.response.redirect(next_url, trusted=True)
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            # authorize form
            return AuthorizeForm(self.context, self.request, parameters)()
        else:
            # redirect to login form, which will then redirect to the
            # authorize form
            site_url = ui_utils.url.absoluteURL(getSite(), self.request)
            self.request.response.redirect(
                site_url+"/login?camefrom=" % self.request.URL)
