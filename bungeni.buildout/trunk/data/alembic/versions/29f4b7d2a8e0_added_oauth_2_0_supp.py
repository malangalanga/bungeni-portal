"""Added OAuth 2.0 support

Revision ID: 29f4b7d2a8e0
Revises: 2df675e61324
Create Date: 2013-03-06 18:56:39.028529

"""

# revision identifiers, used by Alembic.
revision = '29f4b7d2a8e0'
down_revision = '2df675e61324'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('oauth_application',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.UnicodeText(), nullable=False),
    sa.Column('name', sa.UnicodeText(), nullable=False),
    sa.Column('secret', sa.String(length=100), nullable=False),
    sa.Column('redirection_endpoint', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('application_id'),
    sa.UniqueConstraint('identifier')
    )
    op.create_table('oauth_authorization',
    sa.Column('authorization_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('authorization_code', sa.String(length=100), nullable=False),
    sa.Column('expiry', sa.DateTime(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['oauth_application.application_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('authorization_id')
    )
    op.create_table('oauth_access_token',
    sa.Column('access_token_id', sa.Integer(), nullable=False),
    sa.Column('authorization_id', sa.Integer(), nullable=True),
    sa.Column('access_token', sa.String(length=100), nullable=True),
    sa.Column('refresh_token', sa.String(length=100), nullable=True),
    sa.Column('expiry', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['authorization_id'], ['oauth_authorization.authorization_id'], ),
    sa.PrimaryKeyConstraint('access_token_id')
    )


def downgrade():
    op.drop_table('oauth_access_token')
    op.drop_table('oauth_authorization')
    op.drop_table('oauth_application')
