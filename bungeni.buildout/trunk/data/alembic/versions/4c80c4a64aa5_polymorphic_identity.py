"""polymorphic identity column length

Revision ID: 4c80c4a64aa5
Revises: 386ce6463960
Create Date: 2014-05-23 15:00:06.888908 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "4c80c4a64aa5"
down_revision = "386ce6463960"

from alembic import op
import sqlalchemy as sa


def _sql_alter_col_len(_ing, tbl_name, col_name, col_len):
    info = tbl_name, col_name, col_len
    print _ing + " table %r column %r: length -> %s" % info
    return "alter table %s alter column %s type character varying(%s);" % info


def upgrade():
    connection = op.get_bind()
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Upgrading", "change", "action", 128)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Upgrading", "audit", "audit_type", 128)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Upgrading", "principal", "type", 128)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Upgrading", "member", "member_type", 128)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Upgrading", "doc_principal", "activity", 128)))


def downgrade():
    print ("""
        DOWNGRADING COLUMN WIDTH WILL FAIL IF ANY CURRENT VALUE IS LONGER
        THAN THESE (ORIGINAL) REDUCED COLUMN LENGTHS -- IF SUCH DATA EXISTS
        IN THE DB IT MUST BE DELETED FIRST.
        """)
    connection = op.get_bind()
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Downgrading", "change", "action", 16)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Downgrading", "audit", "audit_type", 30)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Downgrading", "principal", "type", 30)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Downgrading", "member", "member_type", 30)))
    connection.execute(sa.sql.text(
            _sql_alter_col_len("Downgrading", "doc_principal", "activity", 16)))



