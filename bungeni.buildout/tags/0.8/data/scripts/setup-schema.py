"""
some database value population scripts
"""

import transaction

from bungeni import models
from bungeni.models import schema
from ore.alchemist import Session
from alchemist import security
from marginalia import schema as marginalia_schema
from sqlalchemy import create_engine

models.metadata.bind = db = create_engine('postgres://localhost/bungeni')
models.metadata.drop_all()
models.metadata.create_all()
# the unbound sequences and indexes wont get created so we have to
# create them maunually
schema.QuestionSequence.create(db)
schema.MotionSequence.create(db)
schema.registrySequence.create(db)
schema.tabled_documentSequence.create(db)
#schema.translation_lookup_index.create(db)

security.metadata.bind = db
security.metadata.drop_all() 
security.metadata.create_all() 

marginalia_schema.metadata.bind = db
marginalia_schema.metadata.drop_all()
marginalia_schema.metadata.create_all() 

db.dispose()

