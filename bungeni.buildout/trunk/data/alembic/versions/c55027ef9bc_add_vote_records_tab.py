"""add vote records table

Revision ID: c55027ef9bc
Revises: 3c88a7f436af
Create Date: 2013-01-17 17:04:35.530198

"""

# revision identifiers, used by Alembic.
revision = 'c55027ef9bc'
down_revision = '3c88a7f436af'

from alembic import op
import sqlalchemy as sa
from bungeni.models.fields import FSBlob


def upgrade():
    op.create_table('item_schedule_vote',
        sa.Column('vote_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime()),
        sa.Column('title', sa.Unicode(length=1024)),
        sa.Column('description', sa.UnicodeText()),
        sa.Column('result', sa.Unicode(length=255)),
        sa.Column('votes_for', sa.Integer()),
        sa.Column('votes_against', sa.Integer()),
        sa.Column('votes_absent', sa.Integer()),
        sa.Column('file', sa.Unicode(length=32)),
        sa.Column('language', sa.Unicode(length=5)),
        sa.PrimaryKeyConstraint('vote_id'),
    )
    op.create_foreign_key("item_schedule_vote_schedule_id_fkey",
        "item_schedule_vote", "item_schedule", ["schedule_id"], ["schedule_id"]
    )


def downgrade():
    op.drop_table("item_schedule_vote")
