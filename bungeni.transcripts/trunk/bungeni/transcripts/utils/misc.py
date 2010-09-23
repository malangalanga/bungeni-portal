from bungeni.models import domain as bungeni_domain
from bungeni.transcripts import domain
from ore.alchemist import Session

def get_assigned_staff(context, role):
    session = Session()
    query = session.query(bungeni_domain.GroupMembership).join(
                (domain.Assignment, 
                    domain.Assignment.staff_id == bungeni_domain.GroupMembership.user_id)).filter(
                domain.Assignment.sitting_id == context.sitting_id)
    results = query.all()
    staff = []
    for ob in results:
        titles = [t.title_name.user_role_name for t in ob.member_titles]
        if role in titles:
            staff.append(ob.user.user_id)
    return staff
