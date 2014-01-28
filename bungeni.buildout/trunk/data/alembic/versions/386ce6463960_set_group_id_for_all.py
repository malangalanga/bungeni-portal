"""group_id configuraition (chamber documents with no group id)

Revision ID: 386ce6463960
Revises: 23e7ea240524
Create Date: 2014-01-28 21:48:29.441174

"""

# revision identifiers, used by Alembic.
revision = '386ce6463960'
down_revision = '23e7ea240524'

from alembic import op
import sqlalchemy as sa


def upgrade():
    connection = op.get_bind()
    print "Setting group_id to chamber_id for all docs with chamber_id"
    connection.execute(sa.sql.text(
        "UPDATE doc SET group_id=chamber_id WHERE "
        "group_id IS NULL and chamber_id IS NOT NULL;"
    ))


def downgrade():
    connection = op.get_bind()
    print "Clear group_id from chamber_id for all docs with chamber_id=group_id"
    connection.execute(sa.sql.text(
        "UPDATE doc SET group_id=NULL "
        "WHERE group_id=chamber_id AND chamber_id IS NOT NULL;"
    ))
