from zope import interface
from zope import schema
from zope.formlib import form
from zope.formlib.namedtemplate import NamedTemplate
from zope.app.component.hooks import getSite
from zope.publisher.browser import BrowserView
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile

import bungeni.ui.utils as ui_utils
from bungeni.core.i18n import _

from bungeni.models.domain import User
from bungeni.alchemist import Session
from zope.component import getUtility
from zope.sendmail.interfaces import ISMTPMailer

from bungeni.models.domain import PasswordRestoreLink
from bungeni.models.utils import get_db_user_id
from bungeni.ui.widgets import HiddenTextWidget

import datetime
import hashlib

SECRET_KEY = "bungeni"

class ILoginForm(interface.Interface):
    login = schema.TextLine(title=_(u"Username"))
    password = schema.Password(title=_(u"Password"))

class Login(form.FormBase):
    form_fields = form.Fields(ILoginForm)
    prefix = ""
    form_name = _(u"Login")
    
    # !+ only used here [ bungeni.ui.login.Login ] ?
    template = ViewPageTemplateFile("templates/login-form.pt")
    
    def __call__(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            app = getSite()
            workspace = app["workspace"]
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(workspace, self.request))
        return super(Login, self).__call__()
            
    @form.action(_(u"Login"))
    def handle_login(self, action, data):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.status = _(u"Invalid account credentials")
        else:
            site_url = ui_utils.url.absoluteURL(getSite(), self.request)
            camefrom = self.request.get('camefrom', site_url+'/')
            self.status = _("You are now logged in")
            self.request.response.redirect( camefrom )

class Logout(BrowserView):
    def __call__( self ):
        self.request.response.expireCookie( "wc.cookiecredentials" )
        site_url = ui_utils.url.absoluteURL(getSite(), self.request)
        self.request.response.redirect( site_url )


class IRestoreLoginForm(interface.Interface):
    email = schema.TextLine(title=_(u"Email"))        

class RestoreLogin(form.FormBase):
    form_fields = form.Fields(IRestoreLoginForm)
    prefix = ""
    form_name = _(u"Restore Login")
    
    template = NamedTemplate("alchemist.form")
    
    def __call__(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            app = getSite()
            workspace = app["workspace"]
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(workspace, self.request))
        
        return super(RestoreLogin, self).__call__()
            
    @form.action(_(u"Restore"))
    def handle_restore(self, action, data):
        email = data.get("email", "")
        if email:
            session = Session()
            user = session.query(User).filter(
                            User.email==email).first()
            if user:
                mailer = getUtility(ISMTPMailer, name="bungeni.smtp")
                self.message = "Your login is '%s'" % user.login
                message = ViewPageTemplateFile("templates/mail.pt")(self)
                mailer.send("admin@bungeni.com", email, message)
                self.status = _(u"Your login was sent to you email.")
            else:
                self.status = _(u"Wrong email address.")


class IRestorePasswordForm(interface.Interface):
    login = schema.TextLine(title=_(u"Username"), required=False)
    email = schema.TextLine(title=_(u"Email"), required=False)
    
class RestorePassword(form.FormBase):
    form_fields = form.Fields(IRestorePasswordForm)
    prefix = ""
    form_name = _(u"Restore Password")
    
    template = NamedTemplate("alchemist.form")
    
    def __call__(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            app = getSite()
            workspace = app["workspace"]
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(workspace, self.request))
            
        return super(RestorePassword, self).__call__()
            
    @form.action(_(u"Restore"))
    def handle_restore(self, action, data):
        site_url = ui_utils.url.absoluteURL(getSite(), self.request)
        login = data.get("login", "")
        email = data.get("email", "")
        user = None
        
        session = Session()
        if email:
            user = session.query(User).filter(
                                User.email==email).first()
        elif login:
            user = session.query(User).filter(
                                User.login==login).first()
            email = user.email
    
        if user:
            link = session.query(PasswordRestoreLink).filter(PasswordRestoreLink.user_id==user.user_id).first()
            if link:
                if not link.expired():
                    self.status = _(u"This user's link is still active!")
                    return
            else:
                link = PasswordRestoreLink()
            
            link.hash = hashlib.sha224(user.login + SECRET_KEY + str(datetime.datetime.now())).hexdigest()
            link.expiration_date = datetime.datetime.now() + datetime.timedelta(1)
            link.user_id = user.user_id
            session.add(link)
                    
            mailer = getUtility(ISMTPMailer, name="bungeni.smtp")
            self.message = "Restore password link: %s/reset_password?key=%s" % (site_url, link.hash)
            message = ViewPageTemplateFile("templates/mail.pt")(self)
            mailer.send("admin@bungeni.com", email, message)
            self.status = _(u"Email was sent!")
            
            
class IResetPasswordForm(interface.Interface):
    password = schema.Password(title=_(u"Password"))
    confirm_password = schema.Password(title=_(u"Confirm Password"))
    key = schema.TextLine(required=False)
    
    @interface.invariant
    def passwordMatch(self):
        if self.password != self.confirm_password:
            raise interface.Invalid(_("Password confirmation failed"))

class ResetPassword(form.FormBase):
    form_fields = form.Fields(IResetPasswordForm)
    form_fields['key'].custom_widget = HiddenTextWidget
    prefix = ""
    form_name = _(u"Reset Password")
    status = ""
    template = NamedTemplate("alchemist.form")
    
    def __init__(self, *args, **kwargs):
        super(ResetPassword, self).__init__(*args, **kwargs)
        key = self.request.get("key",self.request.get("form.key",""))
        self.session = Session()
        self.link = self.session.query(PasswordRestoreLink).filter(
                                PasswordRestoreLink.hash==key).first()
    
    def __call__(self):
        if not self.link:
            self.status = _(u"Wrong key!")
        if self.link and self.link.expired():
            self.status = _(u"Key expired!")
        return super(ResetPassword, self).__call__()
    
    @form.action(_(u"Reset"))
    def handle_reset(self, action, data):
        site_url = ui_utils.url.absoluteURL(getSite(), self.request)
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")
            
        if password and password == confirm_password:
            if not self.link.expired():
                user = self.link.user
                user._password = password
                self.link.expiration_date = datetime.datetime.now()
                self.status = _(u"Password successfully reset!")
            

class IProfileForm(interface.Interface):
    login = schema.TextLine(title=_(u"Username"))
    email = schema.TextLine(title=_(u"Email"))
    password = schema.Password(title=_(u"Password"), required=False)
    confirm_password = schema.Password(title=_(u"Confirm password"), required=False)
    
    @interface.invariant
    def passwordMatch(self):
        if self.password != self.confirm_password:
            raise interface.Invalid(_("Password confirmation failed"))

class Profile(form.FormBase):
    form_fields = form.Fields(IProfileForm)
    prefix = ""
    form_name = _(u"Profile")
    
    # !+ only used here [ bungeni.ui.login.Login ] ?
    template = NamedTemplate("alchemist.form")
    
    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.session = Session()
        user_id = get_db_user_id(self.context)
        self.user = self.session.query(User).filter(User.user_id==user_id).first()
    
    def __call__(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(getSite(), self.request)+'/login')
        return super(Profile, self).__call__()
    
    def setUpWidgets(self, ignore_request=False):
        super(Profile, self).setUpWidgets(ignore_request=ignore_request)
        self.widgets["login"].setRenderedValue(self.user.login)
        self.widgets["email"].setRenderedValue(self.user.email)
   
    @form.action(_(u"Save"))
    def save_profile(self, action, data):
        login = data.get("login","")
        email = data.get("email","")
        password = data.get("password","")
            
        if login:
            users = self.session.query(User).filter(User.login==login)
            if (users.count() == 1 and users.first().user_id == self.user.user_id) or users.count() == 0:
                self.user.login = login
            else:
                self.status = _("Login already taken!")
                return
            
        if email:
            users = self.session.query(User).filter(User.email==email)
            if (users.count() == 1 and users.first().user_id == self.user.user_id) or users.count() == 0:
                self.user.email = email
            else:
                self.status = _("Email already taken!")
                return
            
        if password:
            self.user._password = password
                
        self.status = _("Profile data updated")