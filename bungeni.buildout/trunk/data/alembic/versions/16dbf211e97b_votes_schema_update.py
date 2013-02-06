"""scheduling - vote schema upgrades

Revision ID: 16dbf211e97b
Revises: 477c81e613ac
Create Date: 2013-02-06 14:10:44.165138

"""

# revision identifiers, used by Alembic.
revision = '16dbf211e97b'
down_revision = '477c81e613ac'

from alembic import op
import sqlalchemy as sa

TBL = 'item_schedule_vote'
def upgrade():
    op.add_column(TBL, sa.Column('issue_item', sa.Unicode(length=1024)))
    op.add_column(TBL, sa.Column('issue_sub_item', sa.Unicode(length=1024)))
    op.add_column(TBL, sa.Column('question', sa.Unicode(length=1024)))
    op.add_column(TBL, sa.Column('time', sa.Time(timezone=False)))
    op.add_column(TBL, sa.Column('document_uri', sa.Unicode(length=1024)))
    op.add_column(TBL, sa.Column('notes', sa.UnicodeText()))
    op.add_column(TBL, sa.Column('vote_type', sa.Unicode(length=255)))
    op.add_column(TBL, sa.Column('majority_type', sa.Unicode(length=255)))
    op.add_column(TBL, sa.Column('eligible_votes', sa.Integer()))
    op.add_column(TBL, sa.Column('cast_votes', sa.Integer()))
    op.add_column(TBL, sa.Column('mimetype', sa.Unicode(length=127)))
    op.alter_column(TBL, 'votes_absent', name='votes_abstained')
    op.alter_column(TBL, 'file', name='roll_call')
    op.drop_column(TBL, 'title')
    op.drop_column(TBL, 'date')


def downgrade():
    op.drop_column(TBL, 'issue_item')
    op.drop_column(TBL, 'issue_sub_item')
    op.drop_column(TBL, 'question')
    op.drop_column(TBL, 'time')
    op.drop_column(TBL, 'document_uri')
    op.drop_column(TBL, 'notes')
    op.drop_column(TBL, 'vote_type')
    op.drop_column(TBL, 'majority_type')
    op.drop_column(TBL, 'eligible_votes')
    op.drop_column(TBL, 'cast_votes')
    op.drop_column(TBL, 'mimetype')
    op.alter_column(TBL, 'votes_abstained', name='votes_absent')
    op.alter_column(TBL, 'roll_call', name='file')
    op.add_column(TBL, sa.Column('title', sa.Unicode(length=1024)))
    op.add_column(TBL, sa.Column('date', sa.DateTime(timezone=False)))
