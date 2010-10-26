from bungeni.models import domain
from bungeni.alchemist import Session
import sqlalchemy.sql.expression as sql

def get_assigned_staff(context, role):
    session = Session()
    query = session.query(domain.GroupMembership).join(
                (domain.Assignment, 
                    domain.Assignment.staff_id == domain.GroupMembership.user_id)).filter(
                domain.Assignment.sitting_id == context.sitting_id)
    results = query.all()
    staff = []
    for ob in results:
        titles = [t.title_name.user_role_name for t in ob.member_titles]
        if role in titles:
            staff.append(ob.user.user_id)
    return staff


def get_title_of_user(user_id):
    session = Session()
    transcription_office = session.query(domain.Office).filter(domain.Office.office_type == 'V').all()
    if len(transcription_office) == 0:
        return None
    query = session.query(domain.GroupMembership).filter(
                sql.and_(domain.GroupMembership.membership_type == 'officemember',
                domain.GroupMembership.active_p == True,
                domain.GroupMembership.user_id == user_id,
                domain.GroupMembership.group_id == transcription_office[0].office_id)
                )
    results = query.all()
    if len(results) == 0:
        return None
    ob = results[0]
    titles = [t.title_name.user_role_name for t in ob.member_titles]
    if "Editor" in titles:
        return "Editor"
    if "Reader" in titles:
        return "Reader"
    if "Reporter" in titles:
        return "Reporter"
