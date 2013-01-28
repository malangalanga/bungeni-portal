"""Added unique constraints to group membership tables

Revision ID: 39b2ce245dd4
Revises: 2c3725888762
Create Date: 2013-01-28 18:20:46.603650

"""

# revision identifiers, used by Alembic.
revision = '39b2ce245dd4'
down_revision = '2c3725888762'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("user_group_membership_user_id_group_id_key",
        "user_group_membership", ["user_id", "group_id"])
    op.create_unique_constraint("member_title_membership_id_title_type_id_key",
        "member_title", ["membership_id", "title_type_id"])

def downgrade():
    op.drop_constraint("user_group_membership_user_id_group_id_key",
        "user_group_membership")
    op.drop_constraint("member_title_membership_id_title_type_id_key",
        "member_title",)
