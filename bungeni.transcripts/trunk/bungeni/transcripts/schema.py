#!/usr/bin/env python
# encoding: utf-8
import sqlalchemy as rdb
from sqlalchemy.orm import mapper
from datetime import datetime
metadata = rdb.MetaData()
ItemSequence = rdb.Sequence('item_sequence')
from bungeni.models.schema import make_changes_table
from bungeni.models.schema import make_versions_table

#TranscriptSequence = rdb.Sequence('transcript_id_sequence', metadata)

transcript = rdb.Table(
    "transcript",
    metadata,
    rdb.Column('transcript_id', rdb.Integer, primary_key=True),  
    rdb.Column("person", rdb.UnicodeText),
    rdb.Column("text", rdb.UnicodeText),
    rdb.Column("start_date", rdb.DateTime(timezone=False), nullable=False),
    rdb.Column("end_date", rdb.DateTime(timezone=False), nullable=False),
    rdb.Column("sitting_id", rdb.Integer, nullable=False ),
   )

transcript_changes = make_changes_table( transcript, metadata )
transcript_versions = make_versions_table( transcript, metadata)

sitting = rdb.Table(
    "sitting",
    metadata,
    rdb.Column('sitting_id', rdb.Integer, primary_key=True), 
    rdb.Column('media_path', rdb.UnicodeText, nullable=False), 
    )

takes = rdb.Table(
    "take",
    metadata,
    rdb.Column('take_id', rdb.Integer, primary_key=True),
    rdb.Column('start_date', rdb.DateTime(timezone=False), nullable=False ),
    rdb.Column('end_date', rdb.DateTime(timezone=False), nullable=False),
    rdb.Column('editor_id', rdb.Integer,nullable=False),
    rdb.Column('reader_id', rdb.Integer,nullable=False),
    rdb.Column('reporter_id', rdb.Integer,nullable=False),
    rdb.Column("sitting_id", rdb.Integer, nullable=False ),
    )
    
assignment = rdb.Table(
    "assignment",
    metadata,
    rdb.Column('sitting_id', rdb.Integer, primary_key=True),
    rdb.Column('staff_id', rdb.Integer, primary_key=True),
    )

'''transcriptiongroup = rdb.Table("transcriptiongroup", metadata,
    rdb.Column("transcription_id", rdb.Integer,
        rdb.ForeignKey("groups.group_id"),
        primary_key=True
    )
)   '''     

db = rdb.create_engine('postgres://localhost/bungeni', echo=False)
metadata.bind = db
#metadata.drop_all()
metadata.create_all()


