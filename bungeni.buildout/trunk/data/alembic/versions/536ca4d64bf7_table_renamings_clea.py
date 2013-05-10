"""table renamings/cleanup; drop parliament_members db table (declarative)

Revision ID: 536ca4d64bf7
Revises: c62e9a1aed7
Create Date: 2013-05-10 10:57:23.985453 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "536ca4d64bf7"
down_revision = "c62e9a1aed7"

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    print "Renaming table: group_membership_role -> group_member_role"
    op.rename_table("group_membership_role", "group_member_role", "public")
    print "Renaming table: user_group_membership -> group_member"
    op.rename_table("user_group_membership", "group_member", "public")
    
    # Rename columns (but not associated indices/constraints!)
    print "Renaming table column: group_member: membership_id -> member_id"
    op.alter_column("group_member", "membership_id", new_column_name="member_id")
    print "Renaming table column: group_member: membership_type -> member_type"
    op.alter_column("group_member", "membership_type", new_column_name="member_type")
    print "Renaming table column: member_title: membership_id -> member_id"
    op.alter_column("member_title", "membership_id", new_column_name="member_id")
    print "Renaming table column: group_member_role: membership_id -> member_id"
    op.alter_column("group_member_role", "membership_id", new_column_name="member_id")
    
    # add generic columns to base group_member table
    print "Adding table column: group_member.representation_geo"
    op.add_column("group_member", sa.Column("representation_geo", sa.UnicodeText,
            nullable=True))
    print "Adding table column: group_member.representation_sig"
    op.add_column("group_member", sa.Column("representation_sig", sa.UnicodeText, 
            nullable=True))
    print "Adding table column: group_member.election_type"
    op.add_column("group_member", sa.Column("election_type", sa.Unicode(128),
            server_default="elected", # elected, nominated, ex officio, co-opted, ...
            nullable=True))
    print "Adding table column: group_member.election_date"
    op.add_column("group_member", sa.Column("election_date", sa.Date, 
            server_default=sa.sql.text("now()::date"),
            nullable=True))
    print "Adding table column: group_member.leave_reason"
    op.add_column("group_member", sa.Column("leave_reason", sa.Unicode(40)))
    
    # migrate data from parliament_membership table
    connection = op.get_bind()
    for m in connection.execute(sa.sql.text("""select * from parliament_membership;""")):
        print "Migrating parliament_membership fields: member_id={m.membership_id}".format(m=m)
        q_set = []
        if m.representation:
            q_set.append("representation_geo='{m.representation}'".format(m=m))
        if m.member_election_type:
            q_set.append("election_type='{m.member_election_type}'".format(m=m))
        if m.election_nomination_date:
            q_set.append("election_date='{m.election_nomination_date}'".format(m=m))
        if m.leave_reason:
            q_set.append("leave_reason='{m.leave_reason}'".format(m=m))
        if q_set:
            connection.execute(sa.sql.text(
                    """update group_member set {q_set} """
                    """where member_id={m.membership_id};""".format(
                        q_set=", ".join(q_set),
                        m=m)))
    
    # drop parliament_membership table
    print "Dropping table: parliament_membership"
    op.drop_table("parliament_membership")


def downgrade():

    # Rename columns (but not associated indices/constraints!)
    print "Renaming table column: group_member: member_id -> membership_id"
    op.alter_column("group_member", "member_id", new_column_name="membership_id")
    print "Renaming table column: group_member: member_type -> membership_type"
    op.alter_column("group_member", "member_type", new_column_name="membership_type")
    print "Renaming table column: member_title: member_id -> membership_id"
    op.alter_column("member_title", "member_id", new_column_name="membership_id")
    print "Renaming table column: group_member_role: member_id -> membership_id"
    op.alter_column("group_member_role", "member_id", new_column_name="membership_id")
    
    print "Renaming table: group_member_role -> group_membership_role"
    op.rename_table("group_member_role", "group_membership_role", "public")
    print "Renaming table: group_member -> user_group_membership"
    op.rename_table("group_member", "user_group_membership", "public")
    
    # recreate committee
    print "Re-creating table: parliament_membership"
    sa_tbl_columns = [
        sa.Column("membership_id", sa.Integer,
            sa.ForeignKey("user_group_membership.membership_id"),
            primary_key=True
        ),
        # The region/province/constituency (divisions and order may be in any way 
        # as appropriate for the given parliamentary territory) for the 
        # representation of this member of chamber.
        # Hierarchical Controlled Vocabulary Micro Data Format: 
        # a triple-colon ":::" separated sequence of *key phrase paths*, each of 
        # which is a double-colon "::" separated sequence of *key phrases*.
        sa.Column("representation", sa.UnicodeText, nullable=True),
        # the political party of the MP as of the time he was elected
        sa.Column("party", sa.UnicodeText, nullable=True),
        # is the MP elected, nominated, ex officio member, ...
        sa.Column("member_election_type", sa.Unicode(128),
            default="elected",
            nullable=False,
        ),
        sa.Column("election_nomination_date", sa.Date), # nullable=False),
        sa.Column("leave_reason", sa.Unicode(40)),
    ]
    op.create_table("parliament_membership", *sa_tbl_columns)
    parliament_membership = sa.sql.table("parliament_membership", *sa_tbl_columns)
    
    # populate parliament_membership table
    connection = op.get_bind()
    for m in connection.execute(sa.sql.text(
            """select * from user_group_membership where membership_type='member';""")
        ):
        print "Migrating parliament_membership fields: member_id={m.membership_id}".format(m=m)
        connection.execute(sa.sql.insert(parliament_membership, values=dict(
                        membership_id=m.membership_id,
                        representation=m.representation_geo,
                        party="red", # extended field, just use a hard-value...
                        member_election_type=m.election_type,
                        election_nomination_date=m.election_date,
                        leave_reason=m.leave_reason),
                    inline=True))
    
    # drop generic columns to base user_group_membership table
    print "Dropping table column: user_group_membership.representation_geo"
    op.drop_column("user_group_membership", "representation_geo")
    print "Dropping table column: user_group_membership.representation_sig"
    op.drop_column("user_group_membership", "representation_sig")
    print "Dropping table column: user_group_membership.election_type"
    op.drop_column("user_group_membership", "election_type")
    print "Dropping table column: user_group_membership.election_date"
    op.drop_column("user_group_membership", "election_date")
    print "Dropping table column: user_group_membership.leave_reason"
    op.drop_column("user_group_membership", "leave_reason")


