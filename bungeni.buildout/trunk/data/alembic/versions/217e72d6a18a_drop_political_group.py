"""drop political_group db table (declarative)

Revision ID: 217e72d6a18a
Revises: ec528bf973d
Create Date: 2013-05-06 12:00:46.276066 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "217e72d6a18a"
down_revision = "ec528bf973d"


from alembic import op
import sqlalchemy as sa


VP_OBJECT_TYPE = "group" # vp uses base archetype key


def get_vp_table(name, sa_type):
    return sa.sql.table(name, *[
        sa.Column("object_id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("object_type", sa.String(32), primary_key=True, nullable=False),    
        sa.Column("name", sa.String(50), primary_key=True, nullable=False,),
        sa.Column("value", sa_type),
    ])



def upgrade():
    
    # create "vp_binary" table
    print "Creating vertical property table: %r" % ("vp_binary")
    sa_tbl_columns = [
        sa.Column("object_id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("object_type", sa.String(32), primary_key=True, nullable=False),    
        sa.Column("name", sa.String(50), primary_key=True, nullable=False,),
        sa.Column("value", sa.Binary),
    ]
    op.create_table("vp_binary", *sa_tbl_columns)
    
    # migrate data for existing political groups
    connection = op.get_bind()
    
    # migrate political_group logo fields as vertical properties
    for g in connection.execute(sa.sql.text("""select * from political_group;""")):
        print "Migrating political_group fields: group_id={g.group_id}".format(g=g)
        print "     logo_data"
        vp_binary = get_vp_table("vp_binary", sa.Binary)
        connection.execute(sa.sql.insert(vp_binary, 
                values=dict(
                    object_id=g.group_id,
                    object_type=VP_OBJECT_TYPE,
                    name="logo_data",
                    value=g.logo_data),
                inline=True))
        vp_text = get_vp_table("vp_text", sa.UnicodeText)
        if g.logo_name is not None:
            print "     logo_name"
            connection.execute(sa.sql.insert(vp_text, values=dict(
                        object_id=g.group_id,
                        object_type=VP_OBJECT_TYPE,
                        name="logo_name",
                        value=g.logo_name),
                inline=True))
        if g.logo_mimetype is not None:
            print "     logo_mimetype"
            connection.execute(sa.sql.insert(vp_text, values=dict(
                        object_id=g.group_id,
                        object_type=VP_OBJECT_TYPE,
                        name="logo_mimetype",
                        value=g.logo_mimetype),
                inline=True))
    
    # drop political_group
    print "Dropping table: 'political_group'"
    op.drop_table("political_group")


def downgrade():
    
    # recreate political_group
    print "Re-creating table: 'political_group'"
    sa_tbl_columns = [
        sa.Column("group_id", sa.Integer,
            sa.ForeignKey("group.group_id"), primary_key=True),
        sa.Column("logo_data", sa.Binary),
        sa.Column("logo_name", sa.String(127)),
        sa.Column("logo_mimetype", sa.String(127)),
    ]
    op.create_table("political_group", *sa_tbl_columns)
    political_group = sa.sql.table("political_group", *sa_tbl_columns)
    
    # migrate data for existing political groups
    connection = op.get_bind()
    vp_text = get_vp_table("vp_text", sa.UnicodeText)
    
    # Re-populate political_group table
    for p in connection.execute(sa.sql.text(
                """select * from principal where type='political_group';""")
        ):
        print "Migrating down political_group: group_id={p.principal_id}".format(p=p)
        vp_binary = get_vp_table("vp_binary", sa.Binary)
        logo_data = connection.execute(
                sa.sql.select(vp_binary.c, # columns
                    sa.sql.and_(
                        vp_binary.c.object_id == p.principal_id,
                        vp_binary.c.object_type == VP_OBJECT_TYPE,
                        vp_binary.c.name == "logo_data"))).fetchone()
        logo_name = connection.execute(
                sa.sql.select(vp_text.c, 
                    sa.sql.and_(
                        vp_text.c.object_id == p.principal_id,
                        vp_text.c.object_type == VP_OBJECT_TYPE,
                        vp_text.c.name == "logo_name"))).fetchone()
        logo_mimetype = connection.execute(
                sa.sql.select(vp_text.c, 
                    sa.sql.and_(
                        vp_text.c.object_id == p.principal_id,
                        vp_text.c.object_type == VP_OBJECT_TYPE,
                        vp_text.c.name == "logo_mimetype"))).fetchone()
        # add political_group record
        connection.execute(sa.sql.insert(political_group,
                values=dict(
                        group_id=p.principal_id,
                        logo_data=logo_data and logo_data.value or None,
                        logo_name=logo_name and logo_name.value or None,
                        logo_mimetype=logo_mimetype and logo_mimetype.value or None),
                inline=True))
    
    # clean out any properties on vp_text
    print "Cleaning out any extended properties on 'vp_text'"
    vp_text.delete().where(sa.sql.and_(
            vp_text.c.object_type == VP_OBJECT_TYPE,
            vp_text.c.name in ("logo_name", "logo_mimetype")))
    
    # create "vp_binary" table
    print "Dropping vertical property table: 'vp_binary'"
    op.drop_table("vp_binary")
    

