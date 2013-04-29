"""Merge office table into group table (declarative).

Revision ID: 44568662a025
Revises: 16d750a1ec4b
Create Date: 2013-03-15 18:38:02.708299 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "44568662a025"
down_revision = "35a46050c0d"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table("office")


def downgrade():
    sa_tbl_columns = [
        sa.Column("office_id", sa.Integer,
            sa.ForeignKey("group.group_id"),
            primary_key=True),
    ]
    op.create_table("office", *sa_tbl_columns)
    # pull in data from any existing group offices
    connection = op.get_bind()
    offices = []
    for group in connection.execute(sa.sql.text(
                """select * from public.group where type='office';"""
        )):
        office = dict(office_id=group.group_id)
        print "Migrating down group office: office_id={office_id}".format(**office)
        offices.append(office)
    op.bulk_insert(sa.sql.table("office", *sa_tbl_columns), offices)


