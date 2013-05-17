"""doc renamings

Revision ID: 3bc6466f9cf6
Revises: 536ca4d64bf7
Create Date: 2013-05-16 15:12:02.026702 mr

$Id$
"""

# revision identifiers, used by Alembic.
revision = "3bc6466f9cf6"
down_revision = "536ca4d64bf7"

from alembic import op
import sqlalchemy as sa



'''
                                    Table "public.doc_principal"
    Column    |            Type             |                       Modifiers                        
--------------+-----------------------------+--------------------------------------------------------
 principal_id | integer                     | not null
 doc_id       | integer                     | not null
 activity     | character varying(16)       | not null default 'group_assignment'::character varying
 date         | timestamp without time zone | not null default now()
Indexes:
    "doc_principal_pkey" PRIMARY KEY, btree (doc_id, principal_id, activity)
Foreign-key constraints:
    "doc_principal_doc_id_fkey" FOREIGN KEY (doc_id) REFERENCES doc(doc_id)
    "doc_principal_principal_id_fkey" FOREIGN KEY (principal_id) REFERENCES principal(principal_id)

'''
def upgrade():
    
    print "Renaming tables: "
    print "     group_member_role -> member_role"
    op.rename_table("group_member_role", "member_role", "public")
    print "     group_member -> member"
    op.rename_table("group_member", "member", "public")
    
    print "Reworking table: group_document_assignment -> doc_principal"
    op.rename_table("group_document_assignment", "doc_principal", "public")
    op.drop_constraint("group_document_assignment_doc_id_fkey", "doc_principal")
    op.drop_constraint("group_document_assignment_group_id_fkey", "doc_principal")
    op.drop_constraint("group_document_assignment_pkey", "doc_principal")
    op.add_column("doc_principal",
        sa.Column("activity", sa.Unicode(16), primary_key=True, 
            server_default="group_assignment",
            nullable=False)),
    op.add_column("doc_principal",
        sa.Column("date", sa.DateTime(timezone=False), 
            server_default=sa.sql.text("now()"),
            nullable=False)),
    op.alter_column("doc_principal", "group_id", new_column_name="principal_id")
    op.create_foreign_key("doc_principal_doc_id_fkey",
        "doc_principal", "doc", ["doc_id"], ["doc_id"])
    op.create_foreign_key("doc_principal_principal_id_fkey",
        "doc_principal", "principal", ["principal_id"], ["principal_id"])
    op.create_primary_key("doc_principal_pkey", "doc_principal", 
        ["doc_id", "principal_id", "activity"])

    print "Dropping table: user_doc"
    op.drop_table("user_doc")
    
    print "Dropping table: currently_editing_document"
    op.drop_table("currently_editing_document")
    


'''
Table "public.group_document_assignment"
  Column  |  Type   | Modifiers 
----------+---------+-----------
 group_id | integer | not null
 doc_id   | integer | not null
Indexes:
    "group_document_assignment_pkey" PRIMARY KEY, btree (group_id, doc_id)
Foreign-key constraints:
    "group_document_assignment_doc_id_fkey" FOREIGN KEY (doc_id) REFERENCES doc(doc_id)
    "group_document_assignment_group_id_fkey" FOREIGN KEY (group_id) REFERENCES "group"(group_id)
'''
def downgrade():
    
    print "Renaming tables:"
    print "     member_role -> group_member_role"
    op.rename_table("member_role", "group_member_role", "public")
    print "     member -> group_member"
    op.rename_table("member", "group_member", "public")
    
    print "Reworking table: doc_principal -> group_document_assignment"
    op.drop_constraint("doc_principal_doc_id_fkey", "doc_principal")
    op.drop_constraint("doc_principal_principal_id_fkey", "doc_principal")
    op.drop_constraint("doc_principal_pkey", "doc_principal")
    op.drop_column("doc_principal", "activity"),
    op.drop_column("doc_principal", "date"),
    op.alter_column("doc_principal", "principal_id", new_column_name="group_id")
    op.rename_table("doc_principal", "group_document_assignment", "public")
    op.create_foreign_key("group_document_assignment_doc_id_fkey",
        "group_document_assignment", "doc", ["doc_id"], ["doc_id"])
    op.create_foreign_key("group_document_assignment_group_id_fkey",
        "group_document_assignment", "group", ["group_id"], ["group_id"])
    op.create_primary_key("group_document_assignment_pkey", "group_document_assignment", 
        ["doc_id", "group_id"])
    
    
    print "Re-creating table: user_doc"
    sa_tbl_columns = [
        sa.Column("user_id", sa.Integer,
            sa.ForeignKey("user.user_id"),
            primary_key=True
        ),
        sa.Column("doc_id", sa.Integer,
            sa.ForeignKey("doc.doc_id"),
            primary_key=True
        )
    ]
    op.create_table("user_doc", *sa_tbl_columns)
    
    
    print "Re-creating table: currently_editing_document"
    sa_tbl_columns = [
        sa.Column("user_id", sa.Integer,
            sa.ForeignKey("user.user_id"),
            primary_key=True
        ),
        sa.Column("currently_editing_id", sa.Integer,
            sa.ForeignKey("doc.doc_id"),
            primary_key=True
        ),
        sa.Column("editing_date", sa.DateTime(timezone=False)) 
    ]
    op.create_table("currently_editing_document", *sa_tbl_columns)


