from bungeni.alchemist import Session
from bungeni.models import CurrentlyEditingDocument, User
from bungeni.models.utils import get_db_user_id, get_db_user
from datetime import datetime, timedelta
from zope.publisher.browser import BrowserView
from bungeni.core.interfaces import IPasswordRecoveryTokenUtility
from bungeni.models.domain import PasswordRecoveryToken
from zope.component import getUtility
from bungeni.ui.forms.common import PageForm
from zope import schema, interface
from bungeni.core.i18n import _
from zope.formlib import form
from email.mime.text import MIMEText
import bungeni.ui.utils as ui_utils


class StoreNowEditView(BrowserView):
    """View that is periodically called
    with ajax requests to store the document
    id that the user is being currently
    editing"""

    def __call__(self):
        session = Session()

        # Current logged in user id
        user_id = get_db_user_id(self.context)

        # Looking if there is appropriate object to store
        # currently editing document data
        currently_editing_document = session.query(CurrentlyEditingDocument)\
                                            .filter(CurrentlyEditingDocument.user_id == user_id)\
                                            .first()

        # If not creating one for the current user
        if not currently_editing_document:
            currently_editing_document = CurrentlyEditingDocument()
            currently_editing_document.user_id = user_id
            session.add(currently_editing_document)

        # Assigning current document id
        document_id = self.context.parliamentary_item_id
        currently_editing_document.currently_editing_id = document_id

        # And the current date and time
        current_datetime = datetime.now()
        ago_datetime = current_datetime - timedelta(seconds=20)
        currently_editing_document.editing_date = current_datetime


        # Fetching amount of users that are being editing the document
        # taking into account that last time the ajax request was sent
        # no longer than 20 seconds ago
        count = session.query(CurrentlyEditingDocument)\
                       .filter(CurrentlyEditingDocument.currently_editing_id == document_id)\
                       .filter(CurrentlyEditingDocument.user_id != user_id)\
                       .filter(CurrentlyEditingDocument.editing_date.between(ago_datetime, current_datetime))\
                       .count()

        # Returning the amount, excluding current document editing
        return str(count)


class RecoverPasswordForm(PageForm):
    """ Form to change user password
    """

    class IPassRecoveryForm(interface.Interface):
        password = schema.Password(title=_(u"Password"),
                               required=True)
        retyped_password = schema.Password(title=_(u"Retype password"),
                               required=True)    
    form_fields = form.Fields(IPassRecoveryForm)

    @form.action(_(u"Reset"))
    def handle_reset(self, action, data):
        password = data.get("password", "")
        retyped_password = data.get("retyped_password", "")
        
        if password and retyped_password==password:
            session = Session()
            token = self.request.get("token", "")
            db_token = session.query(PasswordRecoveryToken)\
                              .filter(PasswordRecoveryToken.token == token)\
                              .first()
            user = db_token.user
            # TODO save password 
            
    def __call__(self):
        utility = getUtility(IPasswordRecoveryTokenUtility)
        session = Session()
        token = self.request.get("token", "")
        if token:
            db_token = session.query(PasswordRecoveryToken)\
                              .filter(PasswordRecoveryToken.token == token)\
                              .first()
            if not db_token:
                return "ERROR! INVALID TOKEN!"
            if utility.expired(db_token):
                return "ERROR! TOKEN EXPIRED!"
        else:
            return "ERROR! NO DATA!"
        
        return super(RecoverPasswordForm, self).__call__() 
        


class SendPasswordRecoveryLinkForm(PageForm):
    """Form to generate token and send it to the user."""

    class IPassRecoveryForm(interface.Interface):
        login = schema.TextLine(title=_(u"Login"),
                               required=False)
        email = schema.TextLine(title=_(u"Email"),
                               required=False)
            
    form_fields = form.Fields(IPassRecoveryForm)

    @form.action(_(u"Send"))
    def handle_send(self, action, data):
        session = Session()
        utility = getUtility(IPasswordRecoveryTokenUtility)
        email = data.get("email", "")
        login = data.get("login", "")
            
        if login:
            user = session.query(User).filter(User.login==login).first()
        else:
            user = session.query(User).filter(User.email==email).first()
        if user:
            token = utility.get_token(user)
            if token:
                if not utility.expired(token):
                    return "Your old link haven't expired yet" 
            token = utility.generate_token(user)
            base_url = ui_utils.url.absoluteURL(getSite(), self.request) 
            
            text = "Password recovery link:" + base_url + "/recover-password?token="+token.token
            msg = MIMEText(text)
            msg["Subject"] = "Password recovery"
            # this must be changed
            msg["From"] = "support@bungeni.com"
            msg["To"] = user.email
            print msg
            dispatch(msg)