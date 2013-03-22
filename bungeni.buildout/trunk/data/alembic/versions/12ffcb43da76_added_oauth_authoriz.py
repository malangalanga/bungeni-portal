"""Added oauth_authorization_tokens table to support a user having more than one authorization of an application

Revision ID: 12ffcb43da76
Revises: 240a7b3a4cf4
Create Date: 2013-03-22 14:00:52.348607

"""

# revision identifiers, used by Alembic.
revision = '12ffcb43da76'
down_revision = '240a7b3a4cf4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

def upgrade():
    connection = op.get_bind()
    op.create_table('oauth_authorization_token',
        sa.Column('authorization_token_id', sa.Integer(), nullable=False),
        sa.Column('authorization_id', sa.Integer(), nullable=False),
        sa.Column('authorization_code', sa.String(length=100), nullable=False),
        sa.Column('expiry', sa.DateTime(), nullable=False),
        sa.Column('refresh_token', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ['authorization_id'],
            ['oauth_authorization.authorization_id'],),
        sa.PrimaryKeyConstraint('authorization_token_id')
    )
    op.add_column('oauth_access_token',
        sa.Column('authorization_token_id', sa.Integer(), nullable=True))
    select = text("""SELECT authorization_id, authorization_code, expiry,
        refresh_token from oauth_authorization""")
    results = connection.execute(select)
    for result in results:
        insert = text("""INSERT INTO oauth_authorization_token (
            authorization_id, authorization_code, expiry, refresh_token) 
            VALUES (:authorization_id, :authorization_code,
               :expiry, :refresh_token)""")
        connection.execute(insert, authorization_id=result[0],
            authorization_code=result[1], expiry=result[2], refresh_token=result[3])
        select = text("""SELECT authorization_token_id FROM
            oauth_authorization_token WHERE authorization_id=:authorization_id""")
        a_results = connection.execute(select, authorization_id=result[0])
        for a_result in a_results:
            update = text("""UPDATE oauth_access_token SET authorization_token_id = :authorization_token_id WHERE authorization_id = :authorization_id""")
            connection.execute(update, authorization_token_id=a_result[0], authorization_id=result[0])
    op.drop_column('oauth_access_token', u'authorization_id')
    op.drop_column('oauth_authorization', u'expiry')
    op.drop_column('oauth_authorization', u'refresh_token')
    op.drop_column('oauth_authorization', u'authorization_code')


def downgrade():
    connection = op.get_bind()
    op.add_column('oauth_authorization',
        sa.Column(u'authorization_code', sa.VARCHAR(length=100), nullable=True))
    op.add_column('oauth_authorization',
        sa.Column(u'refresh_token', sa.VARCHAR(length=100), nullable=True))
    op.add_column('oauth_authorization',
        sa.Column(u'expiry', postgresql.TIMESTAMP(), nullable=True))
    op.add_column('oauth_access_token',
        sa.Column(u'authorization_id', sa.INTEGER(), nullable=True))
    select = text("""SELECT authorization_id, authorization_code, expiry,
        refresh_token from oauth_authorization_token""")
    results = connection.execute(select)
    for result in results:
        update = text("""UPDATE oauth_authorization SET 
            authorization_code=:authorization_code, refresh_token=:refresh_token,
             expiry=:expiry WHERE authorization_id=:authorization_id""")
        connection.execute(update, authorization_id=result[0], 
            authorization_code=result[1], expiry=result[2],
            refresh_token=result[3])
    op.alter_column('oauth_authorization', 'authorization_code',
        existing_type=sa.VARCHAR(length=100), nullable=False)
    op.alter_column('oauth_authorization', 'refresh_token',
        existing_type=sa.VARCHAR(length=100), nullable=False)
    op.alter_column('oauth_authorization', 'expiry',
        existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('oauth_authorization', 'authorization_id',
        existing_type=sa.INTEGER(), nullable=False)
    op.drop_column('oauth_access_token', 'authorization_token_id')
    op.drop_table('oauth_authorization_token')
