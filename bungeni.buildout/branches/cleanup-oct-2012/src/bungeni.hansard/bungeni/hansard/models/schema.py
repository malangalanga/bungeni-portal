#!/usr/bin/env python
# encoding: utf-8
import sqlalchemy as rdb
from sqlalchemy.orm import mapper
from datetime import datetime
from bungeni.models.schema import make_changes_table
from bungeni.models.schema import make_versions_table

from bungeni.models.schema import metadata

hansards = rdb.Table("hansards", metadata,
    rdb.Column("hansard_id", rdb.Integer,
        primary_key=True
    ),
    rdb.Column("group_sitting_id", rdb.Integer, rdb.ForeignKey("group_sittings.group_sitting_id")),
)

hansard_items = rdb.Table("hansard_items", metadata,
    rdb.Column("hansard_id", rdb.Integer,
        rdb.ForeignKey("hansards.hansard_id"),
    ),
    rdb.Column("hansard_item_id", rdb.Integer, 
        rdb.ForeignKey("parliamentary_items.parliamentary_item_id"),
        primary_key=True),
    rdb.Column("start_date", rdb.DateTime(timezone=False), nullable=False),
    rdb.Column("end_date", rdb.DateTime(timezone=False), nullable=False),
    # type for polymorphic_identity
    rdb.Column("item_type", rdb.String(30), nullable=False),
)

hansard_parliamentary_items = rdb.Table(
    "hansard_parliamentary_items",
    metadata, 
    rdb.Column("hansard_parliamentary_item_id", rdb.Integer,
        rdb.ForeignKey("hansard_items.hansard_item_id"),
        primary_key=True
        ),
    rdb.Column("parliamentary_item_id", rdb.Integer, rdb.ForeignKey("parliamentary_items.parliamentary_item_id")),
   )

hansard_parliamentary_item_changes = make_changes_table( hansard_parliamentary_items, metadata )
hansard_parliamentary_item_versions = make_versions_table( hansard_parliamentary_items, metadata)

#!+ TODO(miano, 26-Oct-2010) : Rethink this....
# Stores the name of the person speaking if they are not currently a bungeni 
# user otherwise stores their user_id
speechs = rdb.Table(
    "speechs",
    metadata, 
    rdb.Column("speech_id", rdb.Integer,
        rdb.ForeignKey("hansard_items.hansard_item_id"),
        primary_key=True
        ),
    rdb.Column("person_id", rdb.Integer, rdb.ForeignKey("users.user_id")),
    rdb.Column("person_name", rdb.UnicodeText, nullable=True),
    rdb.Column("text", rdb.UnicodeText),
   )

speech_changes = make_changes_table( speechs, metadata )
speech_versions = make_versions_table( speechs, metadata)

hansard_media_paths = rdb.Table(
    "hansard_media_paths",
    metadata,
    rdb.Column("hansard_id", rdb.Integer, 
                rdb.ForeignKey("hansards.hansard_id"),
                primary_key=True
                ), 
    rdb.Column("hansard_media_id", rdb.Integer, 
                primary_key=True
                ), 
    rdb.Column("web_optimised_video_path", rdb.UnicodeText, nullable=True),
    rdb.Column("audio_only_path", rdb.UnicodeText, nullable=True),
    rdb.Column("high_quality_video_path", rdb.UnicodeText, nullable=True), 
    )
    
#!+ TODO(miano, 26-Oct-2010) : Hypothetical case where the editors and readers 
# get equal time allocations as reporters
takes = rdb.Table(
    "takes",
    metadata,
    rdb.Column('take_id', rdb.Integer, primary_key=True),
    rdb.Column('start_date', rdb.DateTime(timezone=False), nullable=False ),
    rdb.Column('end_date', rdb.DateTime(timezone=False), nullable=False),
    rdb.Column('editor_id', rdb.Integer,
                rdb.ForeignKey("users.user_id"),
                nullable=False
                ),
    rdb.Column('reader_id', rdb.Integer,
                rdb.ForeignKey("users.user_id"),
                nullable=False,
                ),
    rdb.Column('reporter_id', rdb.Integer,
                rdb.ForeignKey("users.user_id"),
                nullable=False,
                ),
    rdb.Column("group_sitting_id", rdb.Integer,
                rdb.ForeignKey("group_sittings.group_sitting_id"),
                nullable=False,
                ),
    )
    
assignments = rdb.Table(
    "assignments",
    metadata,
    rdb.Column('group_sitting_id./bn', rdb.Integer,
                rdb.ForeignKey("group_sittings.group_sitting_id"),
                primary_key=True,
                ),
    rdb.Column('staff_id', rdb.Integer,
                rdb.ForeignKey("users.user_id"),
                primary_key=True,
                ),
    )
    
if __name__=='__main__':
    from sqlalchemy import create_engine
    engine = create_engine("postgres://localhost/bungeni", echo=False)
    metadata.reflect(bind=engine)
    metadata.bind = engine
    metadata.create_all()


