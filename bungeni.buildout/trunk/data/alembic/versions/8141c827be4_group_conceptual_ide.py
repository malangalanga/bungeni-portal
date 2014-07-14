"""group conceptual identifier

Revision ID: 8141c827be4
Revises: 1e577319a05
Create Date: 2014-06-30 18:58:27.042270 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "8141c827be4"
down_revision = "1e577319a05"

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    for tbl_name in ("group", "group_audit"):
        print "Adding table column: {0}.conceptual_name".format(tbl_name)
        op.add_column(tbl_name,
            sa.Column("conceptual_name", sa.Unicode(64), nullable=True))
        # satisfy not nullable for for existing records
        from sqlalchemy.sql import table, column
        tbl = table(tbl_name, 
            column("conceptual_name"), 
            column("principal_name"),
            column("sub_type"))
        op.execute(tbl.update().values(conceptual_name=tbl.c.principal_name))
        ''' !+SUB_TYPE_CONCEPTUAL
        # for current chambers, set conceptual_name to current sub_type
        conceptual_sub_types = ("higher_house", "lower_house")
        for conceptual_sub_type in conceptual_sub_types:
            op.execute(
                tbl.update(
                    ).where(tbl.c.sub_type == conceptual_sub_type
                    ).values(conceptual_name=tbl.c.sub_type))
        '''
        # now make not nullable
        op.alter_column(tbl_name, "conceptual_name", nullable=False)
        
        print "Renaming table column: {0}: group_mandate -> group_mandate_type".format(tbl_name)
        op.alter_column(tbl_name, "group_mandate", new_column_name="group_mandate_type")


def downgrade():

    for tbl_name in ("group", "group_audit"):
        print "Dropping table column: {0}.conceptual_name".format(tbl_name)
        op.drop_column(tbl_name, "conceptual_name")
        
        print "Renaming table column: {0}: group_mandate_type -> group_mandate".format(tbl_name)
        op.alter_column(tbl_name, "group_mandate_type", new_column_name="group_mandate")



