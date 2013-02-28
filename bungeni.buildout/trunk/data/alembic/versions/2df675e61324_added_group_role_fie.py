"""Added group_role field to group table

Revision ID: 2df675e61324
Revises: 37871066ea0c
Create Date: 2013-02-27 17:38:58.855888

"""

# revision identifiers, used by Alembic.
revision = '2df675e61324'
down_revision = '37871066ea0c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from bungeni.models.schema import group

def upgrade():
    op.add_column('group', sa.Column('group_role', sa.Unicode(length=256)))
    connection = op.get_bind()
    select = text("""SELECT public.group.group_principal_id, zope_principal_role_map.role_id
    FROM public.group, zope_principal_role_map WHERE
    public.group.group_principal_id = zope_principal_role_map.principal_id
    """)
    results = connection.execute(select)
    for result in results:
        print result
        update = text("""UPDATE public.group SET group_role = :group_role WHERE group_principal_id = :group_principal_id""")
        connection.execute(update, group_principal_id=result[0], group_role=result[1])
    null_select = text("""SELECT group_id, short_name from public.group WHERE group_role IS NULL""")
    null_results = connection.execute(null_select)
    if null_results:
        print "------------MIGRATION INCOMPLETE-----------------------------"
        print "Could not infer group role for the following groups"
        print "Group role set to CommitteeMember. Please update manually in the admin"
        print "interface"
    for result in null_results:
        print "Group %s" % (result[1])
        update = text("""UPDATE public.group SET group_role = 'bungeni.CommitteeMember' WHERE group_role is NULL""")
        connection.execute(update)
    op.alter_column("group", "group_role", nullable=False)
    op.drop_column('office', u'office_role')


def downgrade():
    op.add_column('office', sa.Column(u'office_role', sa.VARCHAR(length=256)))
    office_select = text("""SELECT group_id, group_role from public.group WHERE type='office'""")
    connection = op.get_bind()
    office_results = connection.execute(office_select)
    for result in office_results:
        update = text("""UPDATE office SET office_role=:office_role WHERE office_id = :office_id""")
        connection.execute(update, office_id=result[0], office_role=result[1])
    op.drop_column('group', 'group_role')
