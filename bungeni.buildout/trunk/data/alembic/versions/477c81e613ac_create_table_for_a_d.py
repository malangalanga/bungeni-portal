"""Create table for a datetime vertical property.

Revision ID: 477c81e613ac
Revises: 39289ccc37d8
Create Date: 2013-01-31 19:08:01.944470

"""

# revision identifiers, used by Alembic.
revision = "477c81e613ac"
down_revision = "39289ccc37d8"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table("vp_datetime",
        sa.Column("object_id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("object_type", sa.String(32), primary_key=True, nullable=False),
        sa.Column("name", sa.String(50), primary_key=True, nullable=False,),
        sa.Column("value", sa.DateTime(timezone=False)),
    )


def downgrade():
    op.drop_table("vp_datetime")

