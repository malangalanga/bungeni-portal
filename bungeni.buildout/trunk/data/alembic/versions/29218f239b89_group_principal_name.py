"""group principal name

Revision ID: 29218f239b89
Revises: 1c4e533a4e7f
Create Date: 2013-03-19 17:09:14.724352 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "29218f239b89"
down_revision = "1c4e533a4e7f"

from alembic import op
import sqlalchemy as sa


def upgrade():
    # rework "identifier" into "principal_name", not-nullable, unique
    op.alter_column("group", "identifier", name="principal_name", nullable=False)
    op.create_unique_constraint("group_principal_name_key", 
        "group", ["principal_name"])
    # drop "group_principal_id"
    op.drop_index("grp_grpprincipalid_idx")
    op.drop_column("group", "group_principal_id")


def downgrade():
    # rework "principal_name" back
    op.alter_column("group", "principal_name", name="identifier", nullable=True)
    op.drop_constraint("group_principal_name_key", "group")
    # re-add "group_principal_id" column on group
    op.add_column("group",
        sa.Column("group_principal_id", sa.Unicode(50), unique=True, nullable=True))
    op.create_index("grp_grpprincipalid_idx", "group", ["group_principal_id"])
    # re-populate column
    connection = op.get_bind()
    for gpid in connection.execute(sa.sql.text(
                """select public.group.group_id, principal.type from public.group 
                left join principal on public.group.group_id=principal.principal_id;"""
        )):
        grp = dict(group_id=gpid[0], group_principal_id="group.%s.%s" % (gpid[1], gpid[0]))
        print "Downdating group: id={group_id} group_principal_id={group_principal_id}".format(**grp)
        connection.execute(sa.sql.text(
                """ update public.group set group_principal_id='{group_principal_id}' where group_id={group_id};
                """.format(**grp)))
    op.alter_column("group", "group_principal_id", nullable=False)

