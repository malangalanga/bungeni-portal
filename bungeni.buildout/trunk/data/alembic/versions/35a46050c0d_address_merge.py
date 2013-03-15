"""address merge

Revision ID: 35a46050c0d
Revises: 48acd1b17df2
Create Date: 2013-03-14 17:41:52.506236 mr

"""

# revision identifiers, used by Alembic.
revision = "35a46050c0d"
down_revision = "48acd1b17df2"

from alembic import op
import sqlalchemy as sa


def upgrade():
    sa_tbl_columns = [
        sa.Column("address_id", sa.Integer, primary_key=True),
        # user or group address
        sa.Column("principal_id", sa.Integer,
            sa.ForeignKey("principal.principal_id"),
            nullable=False
        ),
        sa.Column("logical_address_type", sa.Unicode(128),
            default=u"office",
            nullable=False,
        ),
        sa.Column("postal_address_type", sa.Unicode(128),
            default=u"street",
            nullable=False,
        ),
        sa.Column("street", sa.Unicode(256), nullable=True),
        sa.Column("city", sa.Unicode(256), nullable=True),
        sa.Column("zipcode", sa.Unicode(20)),
        sa.Column("country_id", sa.String(2),
            sa.ForeignKey("country.country_id"),
            nullable=True
        ),
        sa.Column("phone", sa.Unicode(256)),
        sa.Column("fax", sa.Unicode(256)),
        sa.Column("email", sa.String(512)),
        # Workflow State -> determines visibility
        sa.Column("status", sa.Unicode(16)),
        sa.Column("status_date", sa.DateTime(timezone=False),
            server_default=sa.sql.text("now()"),
            nullable=False
        ),
    ]
    op.create_table("address", *sa_tbl_columns)
    
    # "migrate" user_address and group_address records to address
    connection = op.get_bind()
    address_col_names = ("address_id", "principal_id", "logical_address_type", 
        "postal_address_type", "street", "city", "zipcode", "country_id", 
        "phone", "fax", "email", "status", "status_date")
    addresses = []
    def append_old_address_data_for(principal_type):
        for old_address in connection.execute(sa.sql.text(
                    """SELECT * from %s_address order by address_id;""" % (
                        principal_type))
            ):
            address = dict(zip(address_col_names, old_address))
            print "Migrating old {principal_type} address: address_id={address_id}, " \
                "{principal_type}_id={principal_id}, logical={logical_address_type}, " \
                "postal={postal_address_type}, ...".format(
                    principal_type=principal_type, **address)
            del address["address_id"]
            addresses.append(address)
    append_old_address_data_for("user")
    append_old_address_data_for("group")
    op.bulk_insert(sa.sql.table("address", *sa_tbl_columns), addresses)
    # !+ USER_GROUP_ADDRESS just leaving old tables as-is, as the effort to 
    # round-trip this fairly involved migration is not worth the minor 
    # "back-data" gains (any changes to address AFTER this update would be lost 
    # if ever a downgrade is executed!). Presumably, these tables will be 
    # eventually dropped e.g. when re-initializing the db.
    #
    # upgrade would need: drop the old tables user_address, group_address


def downgrade():
    op.drop_table("address")
    # !+ USER_GROUP_ADDRESS 
    # downgrade would need: re-create old tables user_address, group_address
    # and then re-populate them from address, then drop address


