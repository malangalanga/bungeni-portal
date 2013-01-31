"""Added parliament type column

Revision ID: 39289ccc37d8
Revises: 39b2ce245dd4
Create Date: 2013-01-31 17:19:07.513578

"""

# revision identifiers, used by Alembic.
revision = '39289ccc37d8'
down_revision = '39b2ce245dd4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('parliament', sa.Column('parliament_type', sa.String(length=30), nullable=True))


def downgrade():
    op.drop_column('parliament', 'parliament_type')
