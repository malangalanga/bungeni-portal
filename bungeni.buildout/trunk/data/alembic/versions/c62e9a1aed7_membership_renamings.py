"""membership renamings

Revision ID: c62e9a1aed7
Revises: 145c471c2ec3
Create Date: 2013-05-09 17:33:16.129011 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "c62e9a1aed7"
down_revision = "145c471c2ec3"

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    connection = op.get_bind()
    
    print "Updating membership_type: 'member_of_parliament' -> 'member':"
    connection.execute(sa.sql.text(
            """update user_group_membership set membership_type='member' """
            """where membership_type='member_of_parliament';"""))


def downgrade():
    
    connection = op.get_bind()

    print "Downdating membership_type: 'member' -> 'member_of_parliament':"
    connection.execute(sa.sql.text(
            """update user_group_membership set membership_type='member_of_parliament' """
            """where membership_type='member';"""))

