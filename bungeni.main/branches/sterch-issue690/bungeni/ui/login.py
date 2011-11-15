import datetime
import hashlib
from email.mime.text import MIMEText

from zope import interface
from zope import schema
from zope.formlib import form
from zope.formlib.namedtemplate import NamedTemplate
from zope.publisher.browser import BrowserView
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility
from zope.sendmail.interfaces import ISMTPMailer

from bungeni.models.domain import User
from bungeni.alchemist import Session
from bungeni.models.domain import PasswordRestoreLink
from bungeni.models.utils import get_db_user_id
from bungeni.ui.widgets import HiddenTextWidget
from bungeni.ui import vocabulary
from bungeni.ui import widgets
from bungeni.models import domain
from bungeni.core.i18n import _
from bungeni.models.settings import EmailSettings
from bungeni.core.app import BungeniApp
import bungeni.ui.utils as ui_utils

MIN_AGE = 25
MAX_AGE = 70

from bungeni.ui.constraints import check_email

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
            app = BungeniApp()
            settings = EmailSettings(app)
            session = Session()
            user = session.query(User).filter(
                            User.email==email).first()
            if user:
                mailer = getUtility(ISMTPMailer, name="bungeni.smtp")
                self.message = _(u"Your login is: ") + user.login
                
                text = ViewPageTemplateFile("templates/mail.pt")(self)
                message = MIMEText(text)
                message.set_charset("utf-8")
                message["Subject"] = _(u"Bungeni login restoration")
                message["From"] = settings.default_sender
                mailer.send(settings.default_sender, email, str(message))
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
        
        app = BungeniApp()
        settings = EmailSettings(app)
        
        session = Session()
        if email:
            user = session.query(User).filter(
                                User.email==email).first()
        elif login:
            user = session.query(User).filter(
                                User.login==login).first()
            email = user.email
    
        if user:
            link = session.query(PasswordRestoreLink).filter(
                PasswordRestoreLink.user_id==user.user_id).first()
            if link:
                if not link.expired():
                    self.status = _(u"This user's link is still active!")
                    return
            else:
                link = PasswordRestoreLink()
            
            link.hash = hashlib.sha224(user.login + 
                                       SECRET_KEY + 
                                       str(datetime.datetime.now())).hexdigest()
            link.expiration_date = datetime.datetime.now() + datetime.timedelta(1)
            link.user_id = user.user_id
            session.add(link)
                    
            mailer = getUtility(ISMTPMailer, name="bungeni.smtp")
            
            
            self.message = _(u"Restore password link: ")\
                 + "%s/reset_password?key=%s" % (site_url, link.hash)
            
            text = ViewPageTemplateFile("templates/mail.pt")(self)
            message = MIMEText(text)
            message.set_charset("utf-8")
            message["Subject"] = _(u"Bungeni password restoration")
            message["From"] = settings.default_sender
            
            mailer.send(settings.default_sender, email, str(message))
            self.status = _(u"Email was sent!")
            
            
class IResetPasswordForm(interface.Interface):
    password = schema.Password(title=_(u"Password"))
    confirm_password = schema.Password(title=_(u"Confirm Password"))
    key = schema.TextLine(required=False)

class ResetPassword(form.FormBase):
    form_fields = form.Fields(IResetPasswordForm)
    form_fields["key"].custom_widget = HiddenTextWidget
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
        
        if password.__class__ is not object:
            if password != confirm_password:
                self.status = _(u"Password confirmation failed!")
                return
            
        if password and password == confirm_password:
            if not self.link.expired():
                user = self.link.user
                user._password = password
                self.link.expiration_date = datetime.datetime.now()
                self.status = _(u"Password successfully reset!")


countries = vocabulary.DatabaseSource(domain.Country,
            token_field="country_id",
            title_field="country_name",
            value_field="country_id"
            )


class IProfileForm(interface.Interface):
    first_name = schema.TextLine(title=_(u"First name"))
    last_name = schema.TextLine(title=_(u"Last name"))
    middle_name = schema.TextLine(title=_(u"Middle name"), required=False)
    email = schema.TextLine(title=_(u"Email"),constraint=check_email)
    description = schema.Text(title=_(u"Biographical notes"), required=False)
    gender = schema.Choice(title=_("Gender"), vocabulary=vocabulary.Gender)
    date_of_birth = schema.Date(title=_("Date of Birth"), 
                                min = datetime.datetime.now().date() - \
                                        datetime.timedelta(MAX_AGE*365),
                                max = datetime.datetime.now().date() - \
                                        datetime.timedelta(MIN_AGE*365))
    birth_nationality = schema.Choice(title=_("Nationality at Birth"), 
                                      source=countries)
    birth_country = schema.Choice(title=_("Country of Birth"), 
                                  source=countries)
    current_nationality = schema.Choice(title=_("Current Nationality"), 
                                        source=countries)
    image = schema.Bytes(title=_("Image"))

class Profile(form.FormBase):
    form_fields = form.Fields(IProfileForm)
    
    form_fields["gender"].custom_widget=widgets.CustomRadioWidget
    form_fields["date_of_birth"].custom_widget=widgets.DateWidget
    form_fields["description"].custom_widget=widgets.RichTextEditor
    form_fields["image"].custom_widget=widgets.ImageInputWidget
    
    prefix = ""
    form_name = _(u"Profile")
    
    # !+ only used here [ bungeni.ui.login.Login ] ?
    template = NamedTemplate("alchemist.form")
    
    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.session = Session()
        user_id = get_db_user_id(self.context)
        self.user = self.session.query(User)\
                                .filter(User.user_id==user_id).first()
            
    def __call__(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(
                        getSite(), self.request)+"/login"
                        )
        return super(Profile, self).__call__()
    
    def setUpWidgets(self, ignore_request=False):
        super(Profile, self).setUpWidgets(ignore_request=ignore_request)
        self.widgets["email"].setRenderedValue(self.user.email)
        self.widgets["first_name"].setRenderedValue(self.user.first_name)
        self.widgets["last_name"].setRenderedValue(self.user.last_name)
        self.widgets["middle_name"].setRenderedValue(self.user.middle_name)
        self.widgets["description"].setRenderedValue(self.user.description)
        self.widgets["gender"].setRenderedValue(self.user.gender)
        self.widgets["image"].setRenderedValue(self.user.image)
        self.widgets["date_of_birth"].setRenderedValue(
                                       self.user.date_of_birth)
        self.widgets["birth_nationality"].setRenderedValue(
                                          self.user.birth_nationality)
        self.widgets["birth_country"].setRenderedValue(
                                       self.user.birth_country)
        self.widgets["current_nationality"].setRenderedValue(
                                            self.user.current_nationality)
   
    @form.action(_(u"Save"))
    def save_profile(self, action, data):
        email = data.get("email","")
        first_name = data.get("first_name","")
        last_name = data.get("last_name","") 
        middle_name = data.get("middle_name","")
        description = data.get("description","")
        gender = data.get("gender","")
        image = data.get("image","")
        date_of_birth = data.get("date_of_birth","")
        birth_nationality = data.get("birth_nationality","")
        birth_country = data.get("birth_country","")
        current_nationality = data.get("current_nationality","")
                        
        if email:
            users = self.session.query(User).filter(User.email==email)
            if (users.count() == 1 and users.first().user_id == self.user.user_id) or\
                users.count() == 0:
                self.user.email = email
            else:
                self.status = _("Email already taken!")
                return
            
        if first_name:
            self.user.first_name = first_name
            
        if last_name:
            self.user.last_name = last_name
        
        if middle_name:
            self.user.middle_name = middle_name
        
        if description:
            self.user.description = description
        
        if gender:
            self.user.gender = gender
            
        if date_of_birth:
            self.user.date_of_birth = date_of_birth
            
        if image:
            self.user.image = image
            
        if birth_nationality:
            self.user.birth_nationality = birth_nationality
        
        if birth_country:
            self.user.birth_country = birth_country
        
        if current_nationality:
            self.user.current_nationality = current_nationality
                
        self.status = _("Profile data updated")
        

class IChangePasswordForm(interface.Interface):
    pswd = schema.Password(title=_(u"Password"), required=True)
    confirm_password = schema.Password(title=_(u"Confirm password"),
                                       required=True)

class ChangePasswordForm(form.FormBase):
    form_fields = form.Fields(IChangePasswordForm)
    
    prefix = ""
    form_name = _(u"Change password")
    
    # !+ only used here [ bungeni.ui.login.Login ] ?
    template = NamedTemplate("alchemist.form")
    
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.session = Session()
        user_id = get_db_user_id(self.context)
        self.user = self.session.query(User)\
                                .filter(User.user_id==user_id).first()
            
    def __call__(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.request.response.redirect(
                        ui_utils.url.absoluteURL(
                        getSite(), self.request)+"/login"
                        )
        return super(ChangePasswordForm, self).__call__()
    
    @form.action(_(u"Change password"))
    def save_password(self, action, data):
        password = data.get("pswd","")
        confirm_password= data.get("confirm_password","")
        
        if password:
            if password != confirm_password:
                self.status = _("Password confirmation failed")
                return
            self.user._password = password
        
        self.status = _("Password changed")
