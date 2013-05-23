"""group/member audit

Revision ID: 23e7ea240524
Revises: 3bc6466f9cf6
Create Date: 2013-05-20 15:54:57.421074 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "23e7ea240524"
down_revision = "3bc6466f9cf6"

from alembic import op
import sqlalchemy as sa

from datetime import datetime
from bungeni.models import schema
from bungeni.utils import naming


def upgrade():
    
    def make_audit_table(tbl_name):
        tbl = getattr(schema, tbl_name)
        audit_tbl_name = naming.audit_table_name(tbl_name)
        audit_tbl_columns = schema.get_audit_table_columns(tbl)
        print "Creating audit table:", audit_tbl_name
        op.create_table(audit_tbl_name, *audit_tbl_columns)
    make_audit_table("group")
    make_audit_table("member")
    make_audit_table("doc_principal")
    
    print "Dropping table:",  "item_member_vote"
    op.drop_table("item_member_vote")
    print "Dropping table:",  "item_vote"
    op.drop_table("item_vote")
    
    print "Dropping unique constraint on table column: debate_record_audit.sitting_id"
    op.drop_constraint("debate_record_audit_sitting_id_key", "debate_record_audit")


def downgrade():
    
    def drop_audit_table(audit_tbl_name):
        print "Dropping audit table:", audit_tbl_name
        op.drop_table(audit_tbl_name)
    drop_audit_table(naming.audit_table_name("group"))
    drop_audit_table(naming.audit_table_name("member"))
    drop_audit_table(naming.audit_table_name("doc_principal"))
    
    item_vote_tbl_columns = [
        sa.Column("vote_id", sa.Integer, primary_key=True),
        sa.Column("item_id", sa.Integer, # !+RENAME doc_id
            sa.ForeignKey("doc.doc_id"),
            nullable=False
        ),
        sa.Column("date", sa.Date),
        sa.Column("affirmative_vote", sa.Integer),
        sa.Column("negative_vote", sa.Integer),
        sa.Column("remarks", sa.UnicodeText),
        sa.Column("language", sa.String(5), nullable=False),
    ]
    item_member_vote_tbl_columns = [
        sa.Column("vote_id", sa.Integer,
            sa.ForeignKey("item_vote.vote_id"),
            primary_key=True,
            nullable=False
        ),
        sa.Column("member_id", sa.Integer,
            sa.ForeignKey("user.user_id"),
            primary_key=True,
            nullable=False
        ),
        sa.Column("vote", sa.Boolean),
    ]
    print "Re-create table: item_vote"
    op.create_table("item_vote", *item_vote_tbl_columns)
    print "Re-create table: item_member_vote"
    op.create_table("item_member_vote", *item_member_vote_tbl_columns)
    
    print "Re-adding unique constraint on table column: debate_record_audit.sitting_id"
    op.create_unique_constraint("debate_record_audit_sitting_id_key", 
        "debate_record_audit", ["sitting_id"])

