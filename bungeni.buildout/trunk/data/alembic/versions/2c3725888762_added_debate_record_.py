"""Added debate record db tables

Revision ID: 2c3725888762
Revises: 3c88a7f436af
Create Date: 2013-01-25 18:22:11.352831

"""

# revision identifiers, used by Alembic.
revision = '2c3725888762'
down_revision = '3c88a7f436af'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('debate_record',
    sa.Column('debate_record_id', sa.Integer(), nullable=False),
    sa.Column('sitting_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Unicode(length=32), nullable=True),
    sa.Column('status_date', sa.DateTime(), server_default='now()', nullable=False),
    sa.ForeignKeyConstraint(['sitting_id'], ['sitting.sitting_id'], ),
    sa.PrimaryKeyConstraint('debate_record_id'),
    sa.UniqueConstraint('sitting_id')
    )
    op.create_table('debate_record_item',
    sa.Column('debate_record_item_id', sa.Integer(), nullable=False),
    sa.Column('debate_record_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['debate_record_id'], ['debate_record.debate_record_id'], ),
    sa.PrimaryKeyConstraint('debate_record_item_id')
    )
    op.create_table('debate_media',
    sa.Column('debate_record_id', sa.Integer(), nullable=False),
    sa.Column('media_id', sa.Integer(), nullable=False),
    sa.Column('media_path', sa.UnicodeText(), nullable=False),
    sa.Column('media_type', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['debate_record_id'], ['debate_record.debate_record_id'], ),
    sa.PrimaryKeyConstraint('debate_record_id', 'media_id')
    )
    op.create_table('debate_record_audit',
    sa.Column('audit_id', sa.Integer(), nullable=False),
    sa.Column('debate_record_id', sa.Integer(), nullable=False),
    sa.Column('sitting_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Unicode(length=32), nullable=True),
    sa.Column('status_date', sa.DateTime(), server_default='now()', nullable=False),
    sa.ForeignKeyConstraint(['audit_id'], ['audit.audit_id'], ),
    sa.ForeignKeyConstraint(['debate_record_id'], ['debate_record.debate_record_id'], ),
    sa.PrimaryKeyConstraint('audit_id'),
    sa.UniqueConstraint('sitting_id')
    )
    op.create_table('debate_speech',
    sa.Column('debate_speech_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.UnicodeText(), nullable=True),
    sa.Column('status', sa.Unicode(length=32), nullable=True),
    sa.Column('status_date', sa.DateTime(), server_default='now()', nullable=False),
    sa.Column('language', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['debate_speech_id'], ['debate_record_item.debate_record_item_id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('debate_speech_id'),
    sa.UniqueConstraint('debate_speech_id')
    )
    op.create_table('debate_doc',
    sa.Column('debate_doc_id', sa.Integer(), nullable=False),
    sa.Column('doc_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['debate_doc_id'], ['debate_record_item.debate_record_item_id'], ),
    sa.ForeignKeyConstraint(['doc_id'], ['doc.doc_id'], ),
    sa.PrimaryKeyConstraint('debate_doc_id')
    )
    op.create_table('debate_record_item_audit',
    sa.Column('audit_id', sa.Integer(), nullable=False),
    sa.Column('debate_record_item_id', sa.Integer(), nullable=False),
    sa.Column('debate_record_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['audit_id'], ['audit.audit_id'], ),
    sa.ForeignKeyConstraint(['debate_record_item_id'], ['debate_record_item.debate_record_item_id'], ),
    sa.PrimaryKeyConstraint('audit_id')
    )


def downgrade():
    op.drop_table('debate_record_item_audit')
    op.drop_table('debate_doc')
    op.drop_table('debate_speech')
    op.drop_table('debate_record_audit')
    op.drop_table('debate_media')
    op.drop_table('debate_record_item')
    op.drop_table('debate_record')
