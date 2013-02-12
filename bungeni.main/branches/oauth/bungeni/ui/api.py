import hashlib
from datetime import datetime, timedelta
import urllib
from sqlalchemy.orm.exc import NoResultFound
from zope.formlib import form
from zope import interface
from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserPage
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.component.hooks import getSite
from zope.formlib.namedtemplate import NamedTemplate

from bungeni.ui.i18n import _
from bungeni.ui import forms, widgets
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

    @form.action(_(u"Create Application"), name="create")
    def handle_create_application(self, action, data, validator="validateAdd"):
        oauth_app = domain.OauthApplication()
        oauth_app.application_identifier = data["application_identifier"]
        oauth_app.application_name = data["application_name"]
        oauth_app.redirection_endpoint = data["redirection_endpoint"]
        oauth_app.application_key = self.get_app_key(
            oauth_app.application_identifier,
            oauth_app.application_name)
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


class OauthException(Exception):

    def __init__(self, state=None):
        self.state = state

    @property
    def error(self):
        raise NotImplemented

    @property
    def error_description(self):
        raise NotImplemented


class OauthRedirectException(OauthException):

    def __init__(self, redirect_uri, state=None):
        self.redirect_uri = redirect_uri
        self.state = state


class UnauthorizedClient(OauthException):

    @property
    def error(self):
        return "unauthorized_client"

    @property
    def error_description(self):
        return "The client is not authorized to request an authorization" \
               " code using this method."


class UnsupportedResponseType(OauthRedirectException):
    @property
    def error(self):
        return "unsupported_response_type"

    @property
    def error_description(self):
        return "The authorization server does not support obtaining an" \
               " authorization code using this method."


class AccessDenied(OauthRedirectException):
    @property
    def error(self):
        return "access_denied"

    @property
    def error_description(self):
        return "The resource owner or authorization server denied the" \
               " request."


class InvalidRequest(OauthRedirectException):
    @property
    def error(self):
        return "invalid_request"

    @property
    def error_description(self):
        return "The request is missing a required parameter, includes an" \
               " invalid parameter value, includes a parameter more than" \
               " once, or is otherwise malformed."


class ErrorPage(BungeniBrowserView):
    
    def __init__(self, context, request, error):
        self.error = error
        super(ErrorPage, self).__init__(context, request)

    def __call__(self):
        self.form_name = "Authorization failed : %s" % self.error.error_description
        return self.form_name

class IAuthorizeForm(interface.Interface):
    client_id = schema.TextLine(required=False)
    state = schema.TextLine(required=False)

class AuthorizeForm(form.FormBase):
    form_fields = form.Fields(IAuthorizeForm)
    form_fields["client_id"].custom_widget = widgets.HiddenTextWidget
    form_fields["state"].custom_widget = widgets.HiddenTextWidget
    template = NamedTemplate("alchemist.form")
    form_name = _("authorise_oauth_application",
        default=u"Authorise OAuth Application")

    def __init__(self, context, request, parameters={}):
        self.parameters = parameters
        self.action_url = "/api/oauth/authorize-form"
        super(AuthorizeForm, self).__init__(context, request)

    #@property
    #def action_url():
    #    return "/api/oauth/authorize-form"

    def generate_authorization_code(self, user_id, application_identifier):
        m = hashlib.sha256()
        m.update("%d%s%s" % (user_id, capi.oauth_secret, application_identifier))
        return m.hexdigest()

    def setUpWidgets(self, ignore_request=False):
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=self.parameters if self.parameters else self.request.form,
            ignore_request=ignore_request
        )
        
    @form.action(_(u"Authorize application"), name="authorize")
    def handle_authorize_app(self, action, data):
        session = Session()
        oauth_authorization = domain.OauthAuthorization()
        oauth_authorization.user_id = get_db_user().user_id
        app = session.query(domain.OauthApplication
            ).filter(domain.OauthApplication.application_identifier
                     == data["client_id"]
            ).one()
        oauth_authorization.application_id = app.application_id
        oauth_authorization.authorization_code = self.generate_authorization_code(
            oauth_authorization.user_id, oauth_authorization.application_id)
        oauth_authorization.expiry = datetime.now() + timedelta(
            seconds=capi.oauth_auth_expiry_time)
        session.add(oauth_authorization)
        redirect_uri = app.redirection_endpoint + "?code=" + oauth_authorization.authorization_code
        if data.get("state", None):
            redirect_uri += "&state=" + data["state"]
        self.request.response.redirect(redirect_uri, trusted=True)

    @form.action(_(u"Cancel"), name="cancel")
    def handle_cancel(self, action, data):
        session = Session()
        app = session.query(domain.OauthApplication
            ).filter(domain.OauthApplication.application_identifier
                     == data["client_id"]
            ).one()
        error = UnauthorizedClient(app.redirection_endpoint, data["state"])
        handle_redirect_error(self.request, error)


def handle_redirect_error(request, error):
    next_url = "%s?error=%s&error_description=%s" % (error.redirect_uri,
                error.error, error.error_description)
    if error.state:
        next_url = next_url + "&state=%s" % (error.state)
    return request.response.redirect(next_url, trusted=True)


class APIOauthAuthorization(BrowserPage):

    def process_parameters(self):
        session = Session()
        parameters = {}

        parameters["state"] = self.request.form.get("state", None)
        
        if self.request.form.get("client_id", None):
            try:
                application = session.query(domain.OauthApplication
                    ).filter(domain.OauthApplication.application_identifier ==
                        self.request.form.get("client_id")
                    ).one()
                parameters["client_id"] = application.application_identifier
                parameters["redirect_uri"] = application.redirection_endpoint
            except NoResultFound:
                raise UnauthorizedClient(parameters["state"])
        else:
            raise UnauthorizedClient(parameters["state"])

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
        except OauthRedirectException as e:
            return handle_redirect_error(self.request, e)

        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            # authorize form
            return AuthorizeForm(self.context, self.request, parameters)()
        else:
            # redirect to login form, which will then redirect back to this
            # page
            site_url = url.absoluteURL(getSite(), self.request)
            redirect_url = self.request.getURL() +"?"+ urllib.urlencode(self.request.form)
            self.request.response.redirect(
                site_url+"/login?camefrom=" + urllib.quote(redirect_url))
