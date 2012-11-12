"""renamed all tables to singular

Revision ID: 4e5c72f22b06
Revises: None
Create Date: 2012-10-03 11:43:15.247340

"""

# revision identifiers, used by Alembic.
revision = '4e5c72f22b06'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table("users", "user")
    op.rename_table("countries", "country")
    op.rename_table("admin_users", "admin_user")
    op.rename_table("user_delegations", "user_delegation")
    op.rename_table("parliament_memberships", "parliament_membership")
    op.rename_table("groups", "group")
    op.rename_table("offices", "office")
    op.rename_table("parliaments", "parliament")
    op.rename_table("committees", "committee")
    op.rename_table("title_types", "title_type")
    op.rename_table("user_group_memberships", "user_group_membership")
    op.rename_table("member_titles", "member_title")
    op.rename_table("group_addresses", "group_address")
    op.rename_table("user_addresses", "user_address")
    op.rename_table("sessions", "session")
    op.rename_table("headings", "heading")
    op.rename_table("venues", "venue")
    
    op.rename_table("item_votes", "item_vote")
    op.execute("ALTER TABLE item_vote RENAME COLUMN affirmative_votes to affirmative_vote")
    op.execute("ALTER TABLE item_vote RENAME COLUMN negative_votes to negative_vote")
    op.rename_table("item_member_votes", "item_member_vote")
    op.rename_table("item_schedules", "item_schedule")
    op.rename_table("item_schedule_discussions", "item_schedule_discussion")
    op.rename_table("settings", "setting")
    op.drop_index("settings_propsheet_idx")
    op.create_index("setting_propsheet_idx", "setting", ["propertysheet"])
    op.rename_table("translations", "translation")
    op.drop_index("translation_lookup_index")
    op.create_index("translation_lookup_index", "translation",
        ["object_id", "object_type", "lang"])
        
def downgrade():
    op.rename_table("user", "users")
    op.rename_table("country", "countries")
    op.rename_table("admin_user", "admin_users")
    op.rename_table("user_delegation", "user_delegations")
    op.rename_table("parliament_membership", "parliament_memberships")
    op.rename_table("group", "groups")
    op.rename_table("office", "offices")
    op.rename_table("parliament", "parliaments")
    op.rename_table("committee", "committees")
    op.rename_table("title_type", "title_types")
    op.rename_table("user_group_membership", "user_group_memberships")
    op.rename_table("member_title", "member_titles")
    op.rename_table("group_address", "group_addresses")
    op.rename_table("user_address", "user_addresses")
    op.rename_table("session", "sessions")
    op.rename_table("heading", "headings")
    op.rename_table("venue", "venues")
    op.rename_table("item_vote", "item_votes")
    op.execute("ALTER TABLE item_votes RENAME COLUMN affirmative_vote to affirmative_votes")
    op.execute("ALTER TABLE item_votes RENAME COLUMN negative_vote to negative_votes")
    op.rename_table("item_member_vote", "item_member_votes")
    op.rename_table("item_schedule", "item_schedules")
    op.rename_table("item_schedule_discussion", "item_schedule_discussions")
    op.rename_table("setting", "settings")
    op.drop_index("setting_propsheet_idx")
    op.create_index("settings_propsheet_idx", "settings", ["propertysheet"])
    op.rename_table("translation", "translations")
    op.drop_index("translation_lookup_index")
    op.create_index("translation_lookup_index", "translations",
        ["object_id", "object_type", "lang"])
