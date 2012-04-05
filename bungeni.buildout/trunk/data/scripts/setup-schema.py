"""
some database value population scripts
"""

from bungeni.alchemist import Session
from bungeni.alchemist import security
from bungeni import models
from bungeni.models import schema

# load the workflows--adjusts the model with features as per each workflow
from bungeni.core.workflows import adapters

from marginalia import schema as marginalia_schema
from sqlalchemy import create_engine

schema.metadata.bind = db = create_engine('postgres://localhost/bungeni')
schema.metadata.drop_all()
schema.metadata.create_all()
# the unbound sequences and indexes wont get created so we have to
# create them maunually
schema.QuestionSequence.create(db)
#!+schema.MotionSequence.create(db)
schema.RegistrySequence.create(db)
schema.tabled_documentSequence.create(db)
#schema.translation_lookup_index.create(db)

#additional sequences for registry numbers
schema.AgendaItemRegistrySequence.create(db)
schema.QuestionRegistrySequence.create(db)
schema.MotionRegistrySequence.create(db)
schema.BillRegistrySequence.create(db)
schema.TabledDocumentRegistrySequence.create(db)
schema.ReportRegistrySequence.create(db)

security.metadata.bind = db
security.metadata.drop_all() 
security.metadata.create_all() 

marginalia_schema.metadata.bind = db
marginalia_schema.metadata.drop_all()
marginalia_schema.metadata.create_all() 

db.dispose()

