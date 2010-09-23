from bungeni.ui.vocabulary import SpecializedSource
from zope.schema import vocabulary
from ore.alchemist import Session
from zope.schema.interfaces import IVocabularyFactory
from zope import interface
from bungeni.models import domain
import sqlalchemy.sql.expression as sql

def ActiveUsers(context, role=None):
    session= Session()
    terms = []
    transcription_office = session.query(domain.Office).filter(domain.Office.office_type == 'V').all()
    if len(transcription_office) == 0:
        return vocabulary.SimpleVocabulary( terms )
    if role == None:
        return vocabulary.SimpleVocabulary( terms )
    query = session.query(domain.GroupMembership).filter(
                sql.and_(domain.GroupMembership.membership_type == 'officemember',
                domain.GroupMembership.active_p == True,
                domain.GroupMembership.group_id == transcription_office[0].office_id)
                )
    results = query.all()
    for ob in results:
        titles = [t.title_name.user_role_name for t in ob.member_titles]
        if role in titles:
            obj = ob.user
            terms.append( 
                vocabulary.SimpleTerm( 
                value = getattr( obj, 'user_id'), 
                token = getattr( obj, 'user_id'),
                title = getattr( obj, 'first_name') + getattr( obj, 'last_name'),
                ))
    return vocabulary.SimpleVocabulary( terms )


def ActiveEditors(context):
    return ActiveUsers(context, 'Editor')

def ActiveReaders(context):
    return ActiveUsers(context, 'Reader')

def ActiveReporters(context):
    return ActiveUsers(context, 'Reporter')
