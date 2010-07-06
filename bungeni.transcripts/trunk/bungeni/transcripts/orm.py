import sqlalchemy as rdb
from sqlalchemy.orm import mapper, relation, column_property, deferred, backref
from bungeni.models import domain as bungeni_domain
from bungeni.models import schema as bungeni_schema
from bungeni.transcripts import schema
from bungeni.transcripts import domain

mapper( domain.Transcript, 
        schema.transcript, 
        properties = { 
                'changes':relation( 
                        domain.TranscriptChange, 
                        backref='origin', 
                        cascade="all,delete-orphan", 
                        passive_deletes=False
                        ) 
                } 
        ) 
        
mapper( domain.TranscriptChange, schema.transcript_changes ) 
mapper( domain.TranscriptVersion, 
        schema.transcript_versions, 
        properties= { 
                'change':relation( domain.TranscriptChange, uselist=False), 
                'head': relation( domain.Transcript, uselist=False) }
       )


mapper( domain.Sitting, schema.sitting, )
mapper( domain.Take, schema.takes, )
mapper( domain.Assignment, schema.assignment, )
