"""Added migration script for change made in r9909 to drop zope_role_permission_map and associated index and to add 
group_document_assignment table

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
    op.drop_table(u'zope_principal_role_map')


def downgrade():
    op.create_table(u'zope_principal_role_map',
        sa.Column(u'principal_id', sa.VARCHAR(length=50), nullable=False),
        sa.Column(u'role_id', sa.VARCHAR(length=50), nullable=False),
        sa.Column(u'setting', sa.BOOLEAN(), nullable=False),
        sa.Column(u'object_type', sa.VARCHAR(length=100), nullable=True),
        sa.Column(u'object_id', sa.INTEGER(), nullable=True),
        sa.PrimaryKeyConstraint()
    )
    op.drop_table('group_document_assignment')
