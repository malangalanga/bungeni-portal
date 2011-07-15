from interfaces import IPasswordRecoveryTokenUtility
from zope.interface import implements
from bungeni.models.domain import PasswordRecoveryToken
from bungeni.alchemist import Session
from datetime import datetime, timedelta
from bungeni.models.utils import get_db_user_id
import hashlib


class PasswordRecoveryTokenUtility():
    implements(IPasswordRecoveryTokenUtility)
    
    def get_token(self, user):
        session = Session()
        token = session.query(PasswordRecoveryToken)\
                       .filter(PasswordRecoveryToken.user_id == user.user_id)\
                       .first()
        print "token", token
        return token

    def generate_token(self, user, expire_time=86400):
        session = Session()
        token = session.query(PasswordRecoveryToken)\
                       .filter(PasswordRecoveryToken.user_id == user.user_id)\
                       .first()
                       
        if not token:
            token = PasswordRecoveryToken()
            token.user_id = user.user_id
            session.add(token)
            
        token.expiration = datetime.now() + timedelta(seconds=expire_time)
        
        sha_token = hashlib.sha224(user.login)
        sha_token.update(user.password)
        sha_token.update(str(token.expiration))
        
        token.token = sha_token.hexdigest()
        return token
        
    def expired(self, token):
        return token.expiration < datetime.now()