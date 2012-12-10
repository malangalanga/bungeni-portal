"""Added time based notifications tables. Stores the scheduled time based notifications

Revision ID: 3c88a7f436af
Revises: 21bb15b184ac
Create Date: 2012-12-10 18:07:42.591002

"""

# revision identifiers, used by Alembic.
revision = '3c88a7f436af'
down_revision = '21bb15b184ac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('time_based_notification',
    sa.Column('notification_id', sa.Integer(), nullable=False),
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('object_type', sa.String(length=50), nullable=False),
    sa.Column('object_status', sa.Unicode(length=32), nullable=True),
    sa.Column('time_string', sa.String(length=50), nullable=False),
    sa.Column('notification_date_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('notification_id', 'object_id', 'object_type', 'time_string')
    )


def downgrade():
    op.drop_table('time_based_notification')
