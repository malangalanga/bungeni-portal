"""Added group_document_assignment table

Revision ID: 21bb15b184ac
Revises: 4e5c72f22b06
Create Date: 2012-10-25 12:38:50.775911

"""

# revision identifiers, used by Alembic.
revision = '21bb15b184ac'
down_revision = '4e5c72f22b06'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('group_document_assignment',
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['doc_id'], ['doc.doc_id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['group.group_id'], ),
        sa.PrimaryKeyConstraint('group_id', 'doc_id')
    )


def downgrade():
    op.drop_table('group_document_assignment')
