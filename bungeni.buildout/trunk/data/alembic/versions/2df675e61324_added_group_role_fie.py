"""Added group_role field to group table

Revision ID: 2df675e61324
Revises: 37871066ea0c
Create Date: 2013-02-27 17:38:58.855888

"""

# revision identifiers, used by Alembic.
revision = '2df675e61324'
down_revision = '37871066ea0c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('group', sa.Column('group_role', sa.Unicode(length=256), nullable=False))
    op.drop_column('office', u'office_role')


def downgrade():
    op.add_column('office', sa.Column(u'office_role', sa.VARCHAR(length=256), nullable=False))
    op.drop_column('group', 'group_role')
