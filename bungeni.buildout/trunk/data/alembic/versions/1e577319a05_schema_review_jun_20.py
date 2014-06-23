"""schema review jun-2014

Revision ID: 1e577319a05
Revises: 4c80c4a64aa5
Create Date: 2014-06-18 18:37:11.208078 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "1e577319a05"
down_revision = "4c80c4a64aa5"

from alembic import op
import sqlalchemy as sa


def sql_alter_col_len(_ing, tbl_name, col_name, col_len):
    info = tbl_name, col_name, col_len
    print _ing + " table UNICODE column LENGTH: %s.%s -> %s" % info
    return sa.sql.text(
        "alter table %s alter column %s type character varying(%s);" % info)


def upgrade():
    
    print "Dropping table column: user.type_of_id"
    op.drop_column("user", "type_of_id")
    
    connection = op.get_bind()
    cx = connection.execute
    cx(sql_alter_col_len("Upgrading", "zope_principal_role_map", "principal_id", 128))
    cx(sql_alter_col_len("Upgrading", "zope_principal_role_map", "object_type", 128))
    cx(sql_alter_col_len("Upgrading", "translation", "object_type", 128))
    cx(sql_alter_col_len("Upgrading", "translation", "field_name", 128))
    cx(sql_alter_col_len("Upgrading", "public.user", "login", 128))
    cx(sql_alter_col_len("Upgrading", "public.group", "principal_name", 128))
    cx(sql_alter_col_len("Upgrading", "public.group_audit", "principal_name", 128))
    cx(sql_alter_col_len("Upgrading", "public.group", "status", 64))
    cx(sql_alter_col_len("Upgrading", "public.group_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "public.group", "acronym", 64))
    cx(sql_alter_col_len("Upgrading", "public.group_audit", "acronym", 64))
    cx(sql_alter_col_len("Upgrading", "member", "status", 64))
    cx(sql_alter_col_len("Upgrading", "member_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "member", "leave_reason", 128))
    cx(sql_alter_col_len("Upgrading", "member_audit", "leave_reason", 128))
    cx(sql_alter_col_len("Upgrading", "sitting", "status", 64))
    cx(sql_alter_col_len("Upgrading", "sitting", "recurring_type", 64))
    cx(sql_alter_col_len("Upgrading", "heading", "status", 64))
    cx(sql_alter_col_len("Upgrading", "address", "status", 64))
    cx(sql_alter_col_len("Upgrading", "attachment", "status", 64))
    cx(sql_alter_col_len("Upgrading", "attachment_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "attachment", "name", 256))
    cx(sql_alter_col_len("Upgrading", "attachment_audit", "name", 256))
    cx(sql_alter_col_len("Upgrading", "attachment", "mimetype", 128))
    cx(sql_alter_col_len("Upgrading", "attachment_audit", "mimetype", 128))
    cx(sql_alter_col_len("Upgrading", "signatory", "status", 64))
    cx(sql_alter_col_len("Upgrading", "signatory_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "title_type", "title_name", 128))
    cx(sql_alter_col_len("Upgrading", "debate_record", "status", 64))
    cx(sql_alter_col_len("Upgrading", "debate_record_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "debate_record_item", "type", 128))
    cx(sql_alter_col_len("Upgrading", "debate_record_item_audit", "type", 128))
    cx(sql_alter_col_len("Upgrading", "debate_speech", "status", 64))
    cx(sql_alter_col_len("Upgrading", "debate_media", "media_type", 128))
    cx(sql_alter_col_len("Upgrading", "debate_take", "debate_take_name", 128))
    cx(sql_alter_col_len("Upgrading", "oauth_application", "secret", 128))
    cx(sql_alter_col_len("Upgrading", "oauth_authorization_token", "authorization_code", 128))
    cx(sql_alter_col_len("Upgrading", "oauth_authorization_token", "refresh_token", 128))
    cx(sql_alter_col_len("Upgrading", "oauth_access_token", "access_token", 128))
    cx(sql_alter_col_len("Upgrading", "item_schedule", "item_type", 128))
    cx(sql_alter_col_len("Upgrading", "item_schedule", "item_status", 128))
    cx(sql_alter_col_len("Upgrading", "item_schedule_vote", "roll_call", 128))
    cx(sql_alter_col_len("Upgrading", "item_schedule_vote", "mimetype", 128))
    cx(sql_alter_col_len("Upgrading", "agenda_text_record", "record_type", 128))
    cx(sql_alter_col_len("Upgrading", "time_based_notification", "object_type", 128))
    cx(sql_alter_col_len("Upgrading", "time_based_notification", "object_status", 64))
    cx(sql_alter_col_len("Upgrading", "time_based_notification", "time_string", 64))
    cx(sql_alter_col_len("Upgrading", "doc", "status", 64))
    cx(sql_alter_col_len("Upgrading", "doc_audit", "status", 64))
    cx(sql_alter_col_len("Upgrading", "doc", "acronym", 64))
    cx(sql_alter_col_len("Upgrading", "doc_audit", "acronym", 64))
    #!+STATUS_NULLABLE
    #print "Altering table column: doc.status -> nullable=False"
    #op.alter_column("doc", "status", nullable=False)
    


def downgrade():
    
    print "Adding table column: user.type_of_id"
    op.add_column("user", sa.Column("type_of_id", sa.String(1)))
    
    print ("""
        DOWNGRADING COLUMN WIDTH WILL FAIL IF ANY CURRENT VALUE IS LONGER
        THAN THESE (ORIGINAL) REDUCED COLUMN LENGTHS -- IF SUCH DATA EXISTS
        IN THE DB IT MUST BE DELETED FIRST.
        """)
    connection = op.get_bind()
    cx = connection.execute
    cx(sql_alter_col_len("Downgrading", "zope_principal_role_map", "principal_id", 50))
    cx(sql_alter_col_len("Downgrading", "zope_principal_role_map", "object_type", 100))
    cx(sql_alter_col_len("Downgrading", "translation", "object_type", 50))
    cx(sql_alter_col_len("Downgrading", "translation", "field_name", 50))
    cx(sql_alter_col_len("Downgrading", "public.user", "login", 80))
    cx(sql_alter_col_len("Downgrading", "public.group", "principal_name", 32))
    cx(sql_alter_col_len("Downgrading", "public.group_audit", "principal_name", 32))
    cx(sql_alter_col_len("Downgrading", "public.group", "status", 32))
    cx(sql_alter_col_len("Downgrading", "public.group_audit", "status", 32))
    cx(sql_alter_col_len("Downgrading", "public.group", "acronym", 32))
    cx(sql_alter_col_len("Downgrading", "public.group_audit", "acronym", 32))
    cx(sql_alter_col_len("Downgrading", "member", "status", 32))
    cx(sql_alter_col_len("Downgrading", "member_audit", "status", 32))
    cx(sql_alter_col_len("Downgrading", "member", "leave_reason", 40))
    cx(sql_alter_col_len("Downgrading", "member_audit", "leave_reason", 40))
    cx(sql_alter_col_len("Downgrading", "sitting", "status", 48))
    cx(sql_alter_col_len("Downgrading", "sitting", "recurring_type", 32))
    cx(sql_alter_col_len("Downgrading", "heading", "status", 32))
    cx(sql_alter_col_len("Downgrading", "address", "status", 16))
    cx(sql_alter_col_len("Downgrading", "attachment", "status", 48))
    cx(sql_alter_col_len("Downgrading", "attachment_audit", "status", 48))
    cx(sql_alter_col_len("Downgrading", "attachment", "name", 200))
    cx(sql_alter_col_len("Downgrading", "attachment_audit", "name", 200))
    cx(sql_alter_col_len("Downgrading", "attachment", "mimetype", 127))
    cx(sql_alter_col_len("Downgrading", "attachment_audit", "mimetype", 127))
    cx(sql_alter_col_len("Downgrading", "signatory", "status", 32))
    cx(sql_alter_col_len("Downgrading", "signatory_audit", "status", 32))
    cx(sql_alter_col_len("Downgrading", "title_type", "title_name", 40))
    cx(sql_alter_col_len("Downgrading", "debate_record", "status", 32))
    cx(sql_alter_col_len("Downgrading", "debate_record_audit", "status", 32))
    cx(sql_alter_col_len("Downgrading", "debate_record_item", "type", 30))
    cx(sql_alter_col_len("Downgrading", "debate_record_item_audit", "type", 30))
    cx(sql_alter_col_len("Downgrading", "debate_speech", "status", 32))
    cx(sql_alter_col_len("Downgrading", "debate_media", "media_type", 100))
    cx(sql_alter_col_len("Downgrading", "debate_take", "debate_take_name", 100))
    cx(sql_alter_col_len("Downgrading", "oauth_application", "secret", 100))
    cx(sql_alter_col_len("Downgrading", "oauth_authorization_token", "authorization_code", 100))
    cx(sql_alter_col_len("Downgrading", "oauth_authorization_token", "refresh_token", 100))
    cx(sql_alter_col_len("Downgrading", "oauth_access_token", "access_token", 100))
    cx(sql_alter_col_len("Downgrading", "item_schedule", "item_type", 30))
    cx(sql_alter_col_len("Downgrading", "item_schedule", "item_status", 64))
    cx(sql_alter_col_len("Downgrading", "item_schedule_vote", "roll_call", 32))
    cx(sql_alter_col_len("Downgrading", "item_schedule_vote", "mimetype", 127))
    cx(sql_alter_col_len("Downgrading", "agenda_text_record", "record_type", 30))
    cx(sql_alter_col_len("Downgrading", "time_based_notification", "object_type", 50))
    cx(sql_alter_col_len("Downgrading", "time_based_notification", "object_status", 32))
    cx(sql_alter_col_len("Downgrading", "time_based_notification", "time_string", 50))
    cx(sql_alter_col_len("Downgrading", "doc", "status", 48))
    cx(sql_alter_col_len("Downgrading", "doc_audit", "status", 48))
    cx(sql_alter_col_len("Downgrading", "doc", "acronym", 48))
    cx(sql_alter_col_len("Downgrading", "doc_audit", "acronym", 48))
    #!+STATUS_NULLABLE
    #print "Altering table column: doc.status -> nullable=True"
    #op.alter_column("doc", "status", nullable=True)


