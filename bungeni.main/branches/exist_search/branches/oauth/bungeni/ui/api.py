import hashlib
import hmac
import random
import string
import urllib
import simplejson
import time
from datetime import datetime, timedelta

from sqlalchemy.orm.exc import NoResultFound
from zope.formlib import form
from zope import interface
from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserPage
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplate

from bungeni.ui.i18n import _
from bungeni.ui import forms, widgets
from bungeni.ui.browser import BungeniBrowserView
from bungeni.capi import capi
from bungeni.models import domain
from bungeni.models.utils import get_db_user
from bungeni.alchemist import Session
from bungeni.ui.utils import url


def get_key():
    """Return a randomly generated key
    """
    m = hashlib.sha1()
    m.update("".join(random.sample(string.letters + string.digits, 20)))
    return m.hexdigest()


class APIDefaultView(BungeniBrowserView):
    def __call__(self):
        return "Bungeni API"


class AddOAuthApplication(forms.common.AddForm):

    @form.action(_(u"Create Application"), name="create")
    def handle_create_application(self, action, data, validator="validateAdd"):
        oauth_app = domain.OAuthApplication()
        oauth_app.identifier = data["identifier"]
        oauth_app.name = data["name"]
        oauth_app.redirection_endpoint = data["redirection_endpoint"]
        oauth_app.secret = get_key()
        session = Session()
        session.add(oauth_app)
        session.flush()
        notify(ObjectCreatedEvent(oauth_app))
        next_url = url.absoluteURL(self.__parent__, self.request)
        self.request.response.redirect(next_url)

    @form.action(_(u"Cancel"), name="cancel")
    def handle_cancel(self, action, data):
        next_url = url.absoluteURL(self.__parent__, self.request)
        self.request.response.redirect(next_url)


class OAuthException(Exception):

    def __init__(self, redirect_uri=None, state=None):
        self.redirect_uri = redirect_uri
        self.state = state

    @property
    def error(self):
        raise NotImplemented

    @property
    def error_description(self):
        raise NotImplemented


class UnauthorizedClient(OAuthException):
    @property
    def error(self):
        return "unauthorized_client"

    @property
    def error_description(self):
        return "The client is not authorized to request an authorization" \
            " code using this method."


class UnsupportedResponseType(OAuthException):
    @property
    def error(self):
        return "unsupported_response_type"

    @property
    def error_description(self):
        return "The authorization server does not support obtaining an" \
            " authorization code using this method."


class AccessDenied(OAuthException):
    @property
    def error(self):
        return "access_denied"

    @property
    def error_description(self):
        return "The resource owner or authorization server denied the" \
            " request."


class InvalidRequest(OAuthException):
    @property
    def error(self):
        return "invalid_request"

    @property
    def error_description(self):
        return "The request is missing a required parameter, includes an" \
            " invalid parameter value, includes a parameter more than" \
            " once, or is otherwise malformed."


class UnsupportedGrantType(OAuthException):
    @property
    def error(self):
        return "unsupported_grant_type"

    @property
    def error_description(self):
        return "The authorization grant type is not supported by the" \
            "authorization server."


class InvalidGrant(OAuthException):
    @property
    def error(self):
        return "invalid_grant"

    @property
    def error_description(self):
        return "The provided authorization grant (e.g. authorization" \
            "code, resource owner credentials) or refresh token is" \
            "invalid, expired, revoked, does not match the redirection" \
            "URI used in the authorization request, or was issued to" \
            "another client."


class ErrorPage(BungeniBrowserView):

    template = ViewPageTemplateFile("templates/error-page.pt")

    def __init__(self, context, request, error):
        self.error = error
        super(ErrorPage, self).__init__(context, request)

    def __call__(self):
        self.error_message = self.error.error_description
        return self.template()


class IOAuthAuthorizeForm(interface.Interface):
    client_id = schema.TextLine(required=False)
    state = schema.TextLine(required=False)
    time = schema.TextLine(required=False)
    nonce = schema.TextLine(required=False)

class OAuthAuthorizeForm(form.FormBase):
    form_fields = form.Fields(IOAuthAuthorizeForm)
    form_fields["client_id"].custom_widget = widgets.HiddenTextWidget
    form_fields["state"].custom_widget = widgets.HiddenTextWidget
    form_fields["nonce"].custom_widget = widgets.HiddenTextWidget
    form_fields["time"].custom_widget = widgets.HiddenTextWidget
    template = NamedTemplate("alchemist.form")
    form_name = _("authorise_oauth_application",
        default=u"Authorise OAuth Application")

    def __init__(self, context, request, parameters={}):
        self.parameters = parameters
        if self.parameters:
            self.parameters["time"] = time.time()
            self.parameters["nonce"] = self.generate_nonce(
                self.parameters["time"])
        self.action_url = "/api/oauth/authorize-form"
        super(OAuthAuthorizeForm, self).__init__(context, request)

    def setUpWidgets(self, ignore_request=False):
        
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=self.parameters if self.parameters else self.request.form,
            ignore_request=ignore_request
        )

    def generate_nonce(self, auth_time):
        data = "{0}:{1}:{2}".format(
            self.parameters["client_id"], get_db_user().user_id, auth_time)
        return hmac.new(capi.oauth_hmac_key, data, hashlib.sha1).hexdigest()

    def check_authorization(self, action, data):
        errors = []
        data = self.request.form
        if not data.get("form.time", None) or not data.get("form.nonce", None):
            errors.append(InvalidRequest)
            return errors
        max_time = datetime.fromtimestamp(float(data["form.time"])) + \
            timedelta(seconds=capi.oauth_authorization_token_expiry_time)
        if (datetime.now() > max_time):
            errors.append(InvalidGrant)
        if data["form.nonce"] != self.generate_nonce(data["form.time"]):
            errors.append(InvalidGrant)
        return errors

    def handle_failure(self, action, data, errors):
        return ErrorPage(self.context, self.request, errors[0])()

    @form.action(_(u"Authorize application"), name="authorize",
        validator=check_authorization, failure=handle_failure)
    def handle_authorize_app(self, action, data):
        session = Session()
        oauth_authorization = domain.OAuthAuthorization()
        oauth_authorization.user_id = get_db_user().user_id
        app = session.query(domain.OAuthApplication
            ).filter(domain.OAuthApplication.identifier ==
                data["client_id"]
            ).one()
        oauth_authorization.application_id = app.application_id
        oauth_authorization.authorization_code = get_key()
        oauth_authorization.expiry = datetime.now() + timedelta(
            seconds=capi.oauth_authorization_token_expiry_time)
        oauth_authorization.active = True
        session.add(oauth_authorization)
        redirect_uri = "{0}?code={1}".format(
            app.redirection_endpoint, oauth_authorization.authorization_code)
        if data.get("state", None):
            redirect_uri = "{0}&state={1}".format(redirect_uri,  data["state"])
        self.request.response.redirect(redirect_uri, trusted=True)

    @form.action(_(u"Cancel"), name="cancel")
    def handle_cancel(self, action, data):
        session = Session()
        app = session.query(domain.OAuthApplication
            ).filter(domain.OAuthApplication.application_identifier
                     == data["client_id"]
            ).one()
        error = UnauthorizedClient(app.redirection_endpoint, data["state"])
        redirect_error(self.context, self.request, error)


def redirect_error(context, request, error):
    if error.redirect_uri:
        next_url = "{0}?error={1}&error_description={2}".format(
            error.redirect_uri, error.error, error.error_description)
        if error.state:
            next_url = "{0}&state={1}".format(next_url, error.state)
        return request.response.redirect(next_url, trusted=True)
    else:
        return ErrorPage(context, request, error)()


def bad_request(context, request, error):
    request.response.setStatus(400)
    data = {"error": error.error, "error_description": error.error_description}
    return simplejson.dumps(data)


class OAuthAuthorization(BrowserPage):

    def process_parameters(self):
        session = Session()
        parameters = {}

        parameters["state"] = self.request.form.get("state", None)

        if self.request.form.get("client_id", None):
            try:
                application = session.query(domain.OAuthApplication
                    ).filter(domain.OAuthApplication.identifier ==
                        self.request.form.get("client_id")
                    ).one()
                parameters["client_id"] = application.identifier
                parameters["redirect_uri"] = application.redirection_endpoint
            except NoResultFound:
                raise UnauthorizedClient(parameters["state"])
        else:
            raise InvalidRequest(parameters["state"])

        if self.request.form.get("client_secret", None):
            if self.request.form.get("client_secret") != application.secret:
                raise UnauthorizedClient(parameters["state"])
        else:
            raise InvalidRequest(parameters["state"])

        if self.request.form.get("response_type", None):
            if self.request.form.get("response_type") != "code":
                raise UnsupportedResponseType(
                    parameters["redirect_uri"], parameters["state"])
            else:
                parameters["response_type"] = "code"
        else:
            raise InvalidRequest(
                parameters["redirect_uri"], parameters["state"])
        return parameters

    def __call__(self):
        try:
            parameters = self.process_parameters()
        except UnauthorizedClient as e:
            return ErrorPage(self.context, self.request, e)()
        except OAuthException as e:
            return redirect_error(self.context, self.request, e)

        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            # authorize form
            return OAuthAuthorizeForm(self.context, self.request, parameters)()
        else:
            # redirect to login form, which will then redirect back to this
            # page
            site_url = url.absoluteURL(getSite(), self.request)
            redirect_url = "{0}?{1}".format(self.request.getURL(),
                urllib.urlencode(self.request.form))
            self.request.response.redirect("{0}/login?camefrom={1}".format(
                site_url, urllib.quote(redirect_url)))


class OAuthAccessToken(BrowserPage):
    authorization = None

    def process_parameters(self):
        parameters = {}
        session = Session()

        if self.request.form.get("client_id", None):
            try:
                application = session.query(domain.OAuthApplication
                    ).filter(domain.OAuthApplication.application_identifier ==
                        self.request.form.get("client_id")
                    ).one()
                parameters["client_id"] = application.application_identifier
            except NoResultFound:
                raise UnauthorizedClient()
        else:
            raise UnauthorizedClient()

        if self.request.form.get("grant_type", None):
            if self.request.form.get("grant_type") != "authorization_code":
                raise UnsupportedGrantType()
            else:
                parameters["response_type"] = "code"
        else:
            raise InvalidRequest()

        if self.request.form.get("code", None):
            try:
                self.authorization = session.query(domain.OAuthAuthorization
                    ).filter(and_(
                        domain.OAuthAuthorization.application_id ==
                        application.application_id,
                        domain.OAuthAuthorization.authorization_code ==
                        self.request.form.get("code")
                        )
                    ).one()
            except NoResultFound:
                raise InvalidGrant()
        else:
            raise UnauthorizedClient()

        if self.authorization.expiry > datetime.now():
            raise InvalidGrant()

        if self.authorization.active is False:
            raise UnauthorizedClient()

    def __call__(self):
        session = Session()
        try:
            parameters = self.parameters()
        except OAuthException as e:
            return bad_request(self.context, self.request, e)
        assert (self.authorization is not None,
            "Authorization object not initalized")
        self.authorization.expiry = datetime.now()
        access_token = domain.OAuthAccessToken()
        access_token.access_token = get_key()
        access_token.refresh_token = get_key()
        self.authorization.access_token = access_token
        session.add(access_token)
        session.flush()
        data = {"access_token": access_token.token_key,
                "token_type": "bearer",
                "expires_in": capi.oauth_access_token_expiry_time,
                "refresh_token": access_token.refresh_token
        }
        return simplejson.dumps(data)
