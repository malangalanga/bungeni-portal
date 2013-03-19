"""One principal type

Combine principal.principal_type and group.type down to principal.type, 
as sqlalchemy seems to have issues with different polymorphic_on columns 
at different levels (base Principal class was polymorphic_on 
principal.c.principal_type while sub-class Group was polymorphic_on 
schema.group.c.type).

Revision ID: 1c4e533a4e7f
Revises: 44568662a025
Create Date: 2013-03-19 12:50:37.871967 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "1c4e533a4e7f"
down_revision = "44568662a025"

from alembic import op
import sqlalchemy as sa


def upgrade():
    # rename "principal_type" to "type" on principal
    op.alter_column("principal", "principal_type", name="type") # !+ 0.5.0 new_column_name="type")
    # update data from existing groups
    connection = op.get_bind()
    for grp in connection.execute(sa.sql.text(
                """select * from public.group order by group_id;"""
        )):
        grp = dict(id_=grp.group_id, type_=grp.type)
        print "Updating principal type: id={id_} type={type_}".format(**grp)
        connection.execute(sa.sql.text(
                """update principal set type='{type_}' where principal_id={id_};
                """.format(**grp)))
    # drop type column on group
    op.drop_column("group", "type")
    
    # drop legacy column on user
    op.drop_column("user", "titles")


def downgrade():
    # add back "type" column on group (nullable for now)
    op.add_column("group", sa.Column("type", sa.String(30), nullable=True))
    # rename "type" back to "principal_type" on principal
    op.alter_column("principal", "type", name="principal_type") # !+ 0.5.0 new_column_name="principal_type")
    # push back data for existing groups
    connection = op.get_bind()
    for grp in connection.execute(sa.sql.text(
                """select * from principal where principal_type != 'user' order by principal_id;"""
        )):
        grp = dict(id_=grp.principal_id, type_=grp.principal_type)
        print "Downdating group type: id={id_} type={type_}".format(**grp)
        connection.execute(sa.sql.text(
                """ update public.group set type='{type_}' where group_id={id_};
                    update principal set principal_type='group' where principal_id={id_};
                """.format(**grp)))
    # now make group.type not nullable
    op.alter_column("group", "type", nullable=False)
    
    # add back legacy column on user
    op.add_column("user", sa.Column("titles", sa.Unicode(32)))


