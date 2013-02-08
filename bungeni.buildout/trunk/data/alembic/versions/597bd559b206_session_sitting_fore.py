"""session sitting foreign key relationship

Revision ID: 597bd559b206
Revises: 16dbf211e97b
Create Date: 2013-02-08 12:53:27.968324

"""

# revision identifiers, used by Alembic.
revision = '597bd559b206'
down_revision = '16dbf211e97b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("sitting", sa.Column("session_id", sa.Integer(), nullable=True))
    op.create_foreign_key("sitting_session_id_fkey",
        "sitting", "session", ["session_id"], ["session_id"]
    )

def downgrade():
    op.drop_constraint("sitting_session_id_fkey", "sitting")
    op.drop_column("sitting", "session_id")
