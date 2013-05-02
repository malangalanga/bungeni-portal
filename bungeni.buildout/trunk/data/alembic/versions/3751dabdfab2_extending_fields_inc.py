"""extending fields - including dublin core metadata and other
descriptive fields.

Revision ID: 3751dabdfab2
Revises: 12ffcb43da76
Create Date: 2013-04-24 11:23:51.929821

$Id$
"""

# revision identifiers, used by Alembic.
revision = "3751dabdfab2"
down_revision = "12ffcb43da76"

from alembic import op
import sqlalchemy as sa


VENUE = "venue"
ATTACHMENT = "attachment"
ATTACHMENT_AUDIT = "attachment_audit"
GROUP = "group"
USER = "user"
DOC = "doc"
DOC_AUDIT = "doc_audit"


def add_doc_columns(table_name):
    op.add_column(table_name, sa.Column("summary", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("sub_title", sa.Unicode(length=1024)))
    op.add_column(table_name, sa.Column("doc_urgency", sa.Unicode(length=128)))
    op.add_column(table_name, sa.Column("doc_date", sa.DateTime(timezone=False)))
    op.add_column(table_name, sa.Column("source_title", sa.Unicode(length=1024)))
    op.add_column(table_name, sa.Column("source_creator", sa.Unicode(length=1024)))
    op.add_column(table_name, sa.Column("source_subject", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_description", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_publisher", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_publisher_address", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_contributors", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_date", sa.DateTime(timezone=False)))
    op.add_column(table_name, sa.Column("source_type", sa.Unicode(length=128)))
    op.add_column(table_name, sa.Column("source_format", sa.Unicode(length=128)))
    op.add_column(table_name, sa.Column("source_doc_source", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_language", sa.Unicode(length=5)))
    op.add_column(table_name, sa.Column("source_relation", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_coverage", sa.UnicodeText()))
    op.add_column(table_name, sa.Column("source_rights", sa.UnicodeText()))

def drop_doc_columns(table_name):
    op.drop_column(table_name, "summary")
    op.drop_column(table_name, "sub_title")
    op.drop_column(table_name, "doc_urgency")
    op.drop_column(table_name, "doc_date")
    op.drop_column(table_name, "source_title")
    op.drop_column(table_name, "source_creator")
    op.drop_column(table_name, "source_subject")
    op.drop_column(table_name, "source_description")
    op.drop_column(table_name, "source_publisher")
    op.drop_column(table_name, "source_publisher_address")
    op.drop_column(table_name, "source_contributors")
    op.drop_column(table_name, "source_date")
    op.drop_column(table_name, "source_type")
    op.drop_column(table_name, "source_format")
    op.drop_column(table_name, "source_doc_source")
    op.drop_column(table_name, "source_language")
    op.drop_column(table_name, "source_relation")
    op.drop_column(table_name, "source_coverage")
    op.drop_column(table_name, "source_rights")

    
def upgrade():
    # venue
    op.add_column(VENUE, sa.Column("body", sa.UnicodeText()))
    
    # attachment
    op.add_column(ATTACHMENT, sa.Column("body", sa.UnicodeText()))
    op.add_column(ATTACHMENT_AUDIT, sa.Column("body", sa.UnicodeText()))
    
    # group
    op.add_column(GROUP, sa.Column("body", sa.UnicodeText()))
    
    # user
    op.add_column(USER, sa.Column("home_language", sa.Unicode(length=5)))
    
    # doc
    add_doc_columns(DOC)
    add_doc_columns(DOC_AUDIT)


def downgrade():
    # venue
    op.drop_column(VENUE, "body")
    
    # attachment
    op.drop_column(ATTACHMENT, "body")
    op.drop_column(ATTACHMENT_AUDIT, "body")
    
    # group
    op.drop_column(GROUP, "body")
    
    # user
    op.drop_column(USER, "home_language")
    
    # doc
    drop_doc_columns(DOC)
    drop_doc_columns(DOC_AUDIT)


