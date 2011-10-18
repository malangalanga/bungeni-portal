from bungeni.core.i18n import _
from bungeni.alchemist import Session
from bungeni.models import domain
import  sqlalchemy as rdb
from zope import component
from bungeni.alchemist.interfaces import IDatabaseEngine
from sqlalchemy import create_engine
# !+ORM_IMPORT(ah, oct-2011)
# The below was added after breakaged in r8689.
# orm is required, but was not directly imported, which broke
# in r8689 
import bungeni.models.orm
from bungeni.models.schema import metadata

def admin_exists():
    # Restricting this script to only adding the first admin user
    session = Session()
    users = session.query(domain.AdminUser).all()
    if len(users) == 0:
        return False
    else:
        return True
        
def login_exists(login):
    session = Session()
    users = session.query(domain.User).filter(
                    domain.User.login==login).all()
    if len(users) == 0:
        return False
    else:
        print _(u"Error : That login exists already")
        return True
        
def check_password(password, confirm_password):
        if password != confirm_password:
            print _(u"Error : Entered password not identical")
            return False
        return True

def add_admin(login, password, email_address):                
    session = Session()
    user = domain.User()
    # The names are hardcorded so that they unambigously refer
    # to the administrator ie. the logs will show "System Administrator" and not
    # 'John Doe'. 
    user.first_name = _(u"System")
    user.last_name = _(u"Administrator")
    user.login = login
    user._password = password
    user.gender = "M"
    user.language = "en"
    user.email=email_address
    user.is_admin = True
    user.active_p = "A" # status, normally automatically set by the workflow
    session.add(user)
    admin_user = domain.AdminUser()
    admin_user.user = user
    session.add(admin_user)
    session.commit()

def main():
    check_login = True
    while check_login:
        login = raw_input(_("Enter admin login name "))
        check_login = login_exists(login)
    check_pass = False
    while not check_pass:
        password = raw_input(_("Enter password "))
        confirm_password = raw_input(_("Confirm password "))
        check_pass = check_password(password, confirm_password)
    email_address = raw_input(_("Enter Email Address "))
    add_admin(login, password, email_address)
    
if __name__ == '__main__':
    db = create_engine('postgres://localhost/bungeni', echo=False)
    component.provideUtility( db, IDatabaseEngine, 'bungeni-db' )
    metadata.bind = db
    if admin_exists():
        print _(u"Administrator account exists already")
    else:
        main()
    
    
