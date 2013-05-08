"""drop committee db table (declarative)

Revision ID: 145c471c2ec3
Revises: 217e72d6a18a
Create Date: 2013-05-07 16:32:02.252497 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "145c471c2ec3"
down_revision = "217e72d6a18a"


from alembic import op
import sqlalchemy as sa


def upgrade():
    
    # create "vp_integer" table
    print "Creating vertical property table: 'vp_integer'"
    sa_tbl_columns = [
        sa.Column("object_id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("object_type", sa.String(32), primary_key=True, nullable=False),    
        sa.Column("name", sa.String(50), primary_key=True, nullable=False,),
        sa.Column("value", sa.Integer),
    ]
    op.create_table("vp_integer", *sa_tbl_columns)
    
    # drop unnecessary custom fields group columns
    op.drop_column("group", "custom1")
    op.drop_column("group", "custom2")
    op.drop_column("group", "custom3")
    op.drop_column("group", "custom4")
    
    # add group columns
    # "group_mandate" column (up from committee.group_continuity)
    op.add_column("group", sa.Column("group_mandate", sa.Unicode(128)))
    
    # migrate data from committee table
    connection = op.get_bind()
    for c in connection.execute(sa.sql.text("""select * from committee;""")):
        print "Migrating committee fields: committee_id={c.committee_id}".format(c=c)
        print "     committee.group_continuity to group.group_mandate: '{c.group_continuity}'".format(c=c)
        connection.execute(sa.sql.text(
                """update public.group set group_mandate='{c.group_continuity}' """
                """where group_id={c.committee_id};""".format(c=c)))
    
    # drop "committee" table
    print "Dropping table: 'committee'"
    op.drop_table("committee")


def downgrade():
    
    # recreate committee
    print "Re-creating table: 'committee'"
    sa_tbl_columns = [
        sa.Column("committee_id", sa.Integer,
            sa.ForeignKey("group.group_id"),
            primary_key=True
        ),
        sa.Column("group_continuity", sa.Unicode(128),
            default="permanent",
            nullable=False,
        ),
        sa.Column("num_members", sa.Integer),
        sa.Column("min_num_members", sa.Integer),
        sa.Column("quorum", sa.Integer),
        sa.Column("num_clerks", sa.Integer),
        sa.Column("num_researchers", sa.Integer),
        sa.Column("proportional_representation", sa.Boolean),
        sa.Column("default_chairperson", sa.Boolean),
        sa.Column("reinstatement_date", sa.Date),
    ]
    op.create_table("committee", *sa_tbl_columns)
    committee = sa.sql.table("committee", *sa_tbl_columns)
    
    # populate committee table
    connection = op.get_bind()
    for g in connection.execute(sa.sql.text(
            """select * from public.group inner join principal on """
            """public.group.group_id=principal.principal_id where """
            """principal.type='committee';""")
        ):
        print "Migrating committee group fields: group_id={g.group_id}".format(g=g)
        print "     group.group_mandate to committee.group_continuity: '{g.group_mandate}'".format(g=g)
        connection.execute(sa.sql.insert(committee, values=dict(
                        committee_id=g.group_id,
                        group_continuity=g.group_mandate,
                        # just use default hard-values for these unusued fields:
                        num_members=12,
                        min_num_members=6,
                        quorum=5,
                        num_clerks=2,
                        num_researchers=4,
                        proportional_representation=True,
                        default_chairperson=None,
                        reinstatement_date=None),
                    inline=True))
    
    # drop group columns
    # "group_mandate" column (up from committee.group_continuity)
    op.drop_column("group", "group_mandate")
    
    # re-add custom fields group columns
    op.add_column("group", sa.Column("custom1", sa.UnicodeText, nullable=True))
    op.add_column("group", sa.Column("custom2", sa.UnicodeText, nullable=True))
    op.add_column("group", sa.Column("custom3", sa.UnicodeText, nullable=True))
    op.add_column("group", sa.Column("custom4", sa.UnicodeText, nullable=True))
    
    # drop "vp_integer" table
    print "Dropping vertical property table: 'vp_integer'"
    op.drop_table("vp_integer")
    
    

