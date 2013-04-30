"""drop parliament table (declarative) 

Revision ID: ec528bf973d
Revises: 3751dabdfab2
Create Date: 2013-04-26 15:23:06.419563 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "ec528bf973d"
down_revision = "3751dabdfab2"

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    # upgrade data for existing parliament groups
    connection = op.get_bind()
    
    # principal.type, "parliament" -> "chamber"
    connection.execute(sa.sql.text(
            """update principal set type='chamber' where type='parliament';"""))
    
    # zope_principal_role_map.object_type, "parliament" -> "chamber"
    connection.execute(sa.sql.text(
            """update zope_principal_role_map set object_type='chamber' where object_type='parliament';"""))
    
    # parliament_type -> group.sub_type
    for p in connection.execute(sa.sql.text("""select * from parliament;""")):
        print "Migrating up parliament group: parliament_id={p.parliament_id}".format(p=p)
        connection.execute(sa.sql.text(
            """update public.group set sub_type='{p.parliament_type}'"""
            """ where group_id={p.parliament_id};""".format(p=p) ))
    
    
    # foreign key columns: parliament.parliament_id -> group.group_id
    # doc
    print 'Reworking "doc" FOREIGN KEY (parliament_id) REFERENCES ' \
        'parliament.parliament_id -> (chamber_id) REFERENCES "group"(group_id)'
    op.drop_constraint("doc_parliament_id_fkey", "doc")
    op.alter_column("doc", "parliament_id", name="chamber_id")
    op.create_foreign_key("doc_chamber_id_fkey",
        "doc", "group", ["chamber_id"], ["group_id"])
    # doc_audit
    op.alter_column("doc_audit", "parliament_id", name="chamber_id")
    # session
    print 'Reworking "session" FOREIGN KEY (parliament_id) REFERENCES ' \
        'parliament.parliament_id -> (chamber_id) REFERENCES "group"(group_id)'
    op.drop_constraint("session_parliament_id_fkey", "session")
    op.alter_column("session", "parliament_id", name="chamber_id")
    op.create_foreign_key("session_chamber_id_fkey",
        "session", "group", ["chamber_id"], ["group_id"])
    
    # drop "parliament" table
    print "Dropping parliament table..."
    op.drop_table("parliament")


def downgrade():
    
    # re-create "parliament" table
    sa_tbl_columns = [
        sa.Column("parliament_id", sa.Integer,
            sa.ForeignKey("group.group_id"),
            primary_key=True
        ),
        sa.Column("parliament_type", sa.String(30), nullable=True),
        sa.Column("election_date", sa.Date, nullable=False),
    ]
    op.create_table("parliament", *sa_tbl_columns)
    
    # downgrade data for existing chamber groups
    connection = op.get_bind()
    
    # principal.type, "chamber" -> "parliament"
    connection.execute(sa.sql.text(
            """update principal set type='parliament' where type='chamber';"""))
    
    # zope_principal_role_map.object_type, "chamber" -> "parliament"
    connection.execute(sa.sql.text(
            """update zope_principal_role_map set object_type='parliament' where object_type='chamber';"""))
    
    # group.sub_type -> parliament_type, capi.legislature.election_date -> parliament.election_date
    from bungeni.capi import capi
    for p in connection.execute(sa.sql.text(
                """select * from principal where type='parliament';""")
        ):
        for g in connection.execute(sa.sql.text(
                    """select * from public.group """
                    """where group_id={p.principal_id};""".format(p=p))
            ):
            print "Migrating down chamber group: group_id={g.group_id}".format(g=g)
            connection.execute(sa.sql.text(
                """insert into parliament (parliament_id, parliament_type, election_date) """
                """values ({g.group_id}, '{g.sub_type}', '{election_date}');""".format(
                    g=g, election_date=capi.legislature.election_date) ))
    
    # foreign key columns: group.group_id -> parliament.parliament_id
    # doc
    print 'Reversing... "doc" FOREIGN KEY (parliament_id) REFERENCES ' \
        'parliament.parliament_id -> (chamber_id) REFERENCES "group"(group_id)'
    op.drop_constraint("doc_chamber_id_fkey", "doc")
    op.alter_column("doc", "chamber_id", name="parliament_id")
    op.create_foreign_key("doc_parliament_id_fkey",
        "doc", "parliament", ["parliament_id"], ["parliament_id"])
    # doc_audit
    op.alter_column("doc_audit", "chamber_id", name="parliament_id")
    # session
    print 'Reversing... "session" FOREIGN KEY (parliament_id) REFERENCES ' \
        'parliament.parliament_id -> (chamber_id) REFERENCES "group"(group_id)'
    op.drop_constraint("session_chamber_id_fkey", "session")
    op.alter_column("session", "chamber_id", name="parliament_id")
    op.create_foreign_key("session_parliament_id_fkey",
        "session", "parliament", ["parliament_id"], ["parliament_id"])



