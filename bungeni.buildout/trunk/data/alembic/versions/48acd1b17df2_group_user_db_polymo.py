"""Group/User db polymorphism.

Revision ID: 48acd1b17df2
Revises: 2df675e61324
Create Date: 2013-03-13 13:07:54.693766 mr

"""

# revision identifiers, used by Alembic.
revision = "48acd1b17df2"
down_revision = "2df675e61324"

from alembic import op
import sqlalchemy as sa


def upgrade():
    # new principal table
    from bungeni.models.schema import PrincipalSequence
    op.create_table("principal",
        sa.Column("principal_id", sa.Integer, PrincipalSequence, primary_key=True),
        sa.Column("principal_type", sa.String(30), nullable=False),
    )
    # "populate" newly created principal table
    connection = op.get_bind()
    connection.execute(sa.sql.text("""
        CREATE FUNCTION populate_principals() RETURNS integer AS $$
            DECLARE pid INTEGER;
            BEGIN
                FOR pid IN select user_id FROM public.user ORDER BY user_id LOOP
                        INSERT INTO principal VALUES (pid, 'user');
                END LOOP;
                FOR pid IN select group_id FROM public.group ORDER BY group_id LOOP
                    INSERT INTO principal VALUES (pid, 'group');
                END LOOP;        
                RETURN 1;
            END;
        $$ LANGUAGE plpgsql;
        SELECT populate_principals();
    """))
    # adjustments to user table
    op.create_foreign_key("user_user_id_fkey",
        "user", "principal", ["user_id"], ["principal_id"])
    # adjustments to group table
    op.create_foreign_key("group_group_id_fkey",
        "group", "principal", ["group_id"], ["principal_id"])
    op.alter_column("group", "group_principal_id", nullable=False)
    op.create_unique_constraint("group_group_principal_id_key", 
        "group", ["group_principal_id"])


def downgrade():
    # user
    op.drop_constraint("user_user_id_fkey", "user")
    # group
    op.drop_constraint("group_group_id_fkey", "group")
    op.alter_column("group", "group_principal_id", nullable=True)
    op.drop_constraint("group_group_principal_id_key", "group")
    # principal
    op.drop_table("principal")


