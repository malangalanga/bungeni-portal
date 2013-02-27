"""bind venues to groups

Revision ID: 37871066ea0c
Revises: 42c0c55f3b7e
Create Date: 2013-02-27 11:44:18.509022

"""

# revision identifiers, used by Alembic.
revision = '37871066ea0c'
down_revision = '42c0c55f3b7e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("venue", sa.Column("group_id", sa.Integer(), nullable=True))
    op.create_foreign_key("venue_group_id_fkey",
        "venue", "group", ["group_id"], ["group_id"]
    )

def downgrade():
    op.drop_constraint("venue_group_id_fkey", "venue")
    op.drop_column("venue", "group_id")
