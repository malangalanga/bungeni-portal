"""adding text record table - used in schedule agendas to store per-instance text records

Revision ID: 42c0c55f3b7e
Revises: 597bd559b206
Create Date: 2013-02-13 15:01:14.550990

"""

# revision identifiers, used by Alembic.
revision = '42c0c55f3b7e'
down_revision = '597bd559b206'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('agenda_text_record',
        sa.Column('text_record_id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.String(length=30)),
        sa.Column('text', sa.UnicodeText()),
        sa.Column('language', sa.Unicode(length=5)),
        sa.PrimaryKeyConstraint('text_record_id'),
    )


def downgrade():
    op.drop_table("agenda_text_record")
