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
    """ Form to change user password. Uses IPasswordRecoveryTokenUtility utility
    to manage expiration and token existance checks.
    """
    
    class ERROR_CODES:
        OK = None
        NO_TOKEN = "no_token"
        BAD_TOKEN = "bad_token"
        EXPIRED_TOKEN = "expired_token"

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
        
        if password and retype_password and retyped_password==password:
            # TODO: We have a new password. Most likely we would want to:
            #    - Test it for valid string.
            # This test is most likely not needed, but it is still a good
            # idea to make shure.
            assert self.test_precondition() is self.ERROR_CODES.OK
            utility = getUtility(IPasswordRecoveryTokenUtility)
            session = Session()
            # We tested the precondition. It is valid.
            token = self.request["token"]
            user = utility.get_user(token)
            
            # TODO: Save password to database
            
            # After we changed the password we expire the token. Do not worry, 
            # its still one transaction.
            utility.expire(token)
            
    def test_precondition(self):
        """ tests if token exists, is_valid and is not expired
            Returns error code:
        """
        utility = getUtility(IPasswordRecoveryTokenUtility)
        session = Session()
        token = self.request.get("token")
        if token is None:
            return self.ERROR_CODES.NO_TOKEN
        # TODO: Maybe we should set a test for token validation. Maybe its a 
        # bad string. We might get an error in the database.
        res = None
        if utility.expired(token):
            return self.ERROR_CODES.EXPIRED_TOKEN
            
    def __call__(self):
        # We test the preconditions to avoid the update call if the precondition
        # did not pass


        if self.test_precondition() is not self.ERROR_CODES.OK:
            # TODO: We must set a redirect or render error page.
            return ""
        
        return super(RecoverPasswordForm, self).__call__() 
        


class SendPasswordRecoveryLinkForm(PageForm):
    """Form to generate token and send it to the user."""

    class IPassRecoveryForm(interface.Interface):
        login_or_email = schema.TextLine(title=_(u"Login or email"),
                                         required=False)
            
    form_fields = form.Fields(IPassRecoveryForm)

    @form.action(_(u"Send"))
    def handle_send(self, action, data):
        session = Session()
        utility = getUtility(IPasswordRecoveryTokenUtility)
        login_or_email = data.get("login_or_email", "")
            
        user = session.query(User).filter(or_(User.login==login_or_email,
                                              User.email==login_or_email)).first()
        if user is not None:
            token = utility.generate_token(user)
            base_url = ui_utils.url.absoluteURL(getSite(), self.request) 
            recovery_url = base_url + "/recover-password?token=" + token.token
            
            # TODO: Isn't there a way to change this template in an easy way(in 
            # admin maybe? Or as a ZPT)
            text = "Password recovery link:" + recovery_url
            msg = MIMEText(text)
            msg["Subject"] = "Password recovery"
            # TODO: this must be changed. There must be a global config for info
            # email.
            msg["From"] = "support@bungeni.com"
            msg["To"] = user.email
            print msg
            dispatch(msg)