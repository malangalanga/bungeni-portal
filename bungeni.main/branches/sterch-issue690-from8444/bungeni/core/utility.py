from interfaces import IPasswordRecoveryTokenUtility
from zope.interface import implements
from bungeni.models.domain import PasswordRecoveryToken
from bungeni.alchemist import Session
from datetime import datetime, timedelta
from bungeni.models.utils import get_db_user_id
import hashlib


class PasswordRecoveryTokenUtility():
    implements(IPasswordRecoveryTokenUtility)
    
    def get_user(self, user):
        session = Session()
        token = session.query(PasswordRecoveryToken)\
                       .filter(PasswordRecoveryToken.token == token)\
                       .first()
        return token.user

    def generate_token(user, expire_time=86400):
        """ Generate new token for user. Cleanups old ones.
        """
        session = Session()
        token = session.query(PasswordRecoveryToken)\
                       .filter(PasswordRecoveryToken.user_id == user.user_id)\
                       .first()

        if token is not None:
            self.expire(token)
            
        token = PasswordRecoveryToken()
        token.user_id = user.user_id
        session.add(token)
            
        token.expiration = datetime.now() + timedelta(seconds=expire_time)
        
        sha_token = hashlib.sha224(user.login)
        sha_token.update(user.password)
        sha_token.update(str(token.expiration))
        
        token.token = sha_token.hexdigest()
        print token.token
        return token
    
    def expired(token):
        """Check if token is expired
        """
        token = session.query(PasswordRecoveryToken)\
                       .filter(PasswordRecoveryToken.token == token)\
                       .first()
        return token.expiration < datetime.now()
        
    def expire(token):
        """Expires token before time
        """
        return session.query(PasswordRecoveryToken)\
                      .filter(PasswordRecoveryToken.token == token)\
                      .delete()