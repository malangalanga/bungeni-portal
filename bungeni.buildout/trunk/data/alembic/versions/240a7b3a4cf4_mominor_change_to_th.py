"""MoMinor change to the OAuth tables to move refresh_token column to OAuthAuthorization table

Revision ID: 240a7b3a4cf4
Revises: 29218f239b89
Create Date: 2013-03-20 17:16:08.647546

"""

# revision identifiers, used by Alembic.
revision = '240a7b3a4cf4'
down_revision = '29218f239b89'

import hashlib
import string
import random
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


def get_key():
    """Return a randomly generated key"""
    m = hashlib.sha1()
    m.update("".join(random.sample(string.letters + string.digits, 20)))
    return m.hexdigest()

def upgrade():
    connection = op.get_bind()
    op.alter_column('oauth_access_token', 'access_token',
        existing_type=sa.VARCHAR(length=100), nullable=False)
    op.add_column('oauth_authorization', sa.Column('refresh_token', sa.String(length=100)))
    select = text("""SELECT authorization_id, refresh_token FROM oauth_access_token""")
    results = connection.execute(select)
    for result in results:
        update = text("""UPDATE oauth_authorization SET refresh_token = :refresh_token WHERE authorization_id = :authorization_id""")
        connection.execute(update, refresh_token=result[1], authorization_id=result[0])
    # update authorizations that have null refresh_token
    # The fact that they are null means they haven't been used yet, so this is ok
    select = text("""SELECT authorization_id FROM oauth_authorization WHERE refresh_token is NULL""")
    results = connection.execute(select)
    for result in results:
        update = text("""UPDATE oauth_authorization SET refresh_token = :refresh_token WHERE authorization_id = :authorization_id""")
        connection.execute(update, refresh_token=get_key(), authorization_id=result[0])
    op.alter_column('oauth_authorization', 'refresh_token',
        existing_type=sa.VARCHAR(length=100), nullable=False)
    op.drop_column('oauth_access_token', u'refresh_token')
               
def downgrade():
    connection = op.get_bind()
    op.add_column('oauth_access_token', sa.Column(u'refresh_token', sa.VARCHAR(length=100)))
    select = text("""SELECT authorization_id, refresh_token FROM oauth_authorization""")
    results = connection.execute(select)
    for result in results:
        update = text("""UPDATE oauth_access_token SET refresh_token = :refresh_token WHERE authorization_id = :authorization_id""")
        connection.execute(update, refresh_token=result[1], authorization_id=result[0])
    op.drop_column('oauth_authorization', 'refresh_token')
    op.alter_column('oauth_access_token', 'access_token',
        existing_type=sa.VARCHAR(length=100),nullable=True)
    
