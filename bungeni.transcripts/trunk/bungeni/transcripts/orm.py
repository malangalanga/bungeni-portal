import sqlalchemy as rdb
from sqlalchemy.orm import mapper, relation, column_property, deferred, backref

import schema
import domain

mapper( domain.Transcript, schema.transcript, )
mapper( domain.Sitting, schema.sitting, )
mapper( domain.Take, schema.takes, )
mapper( domain.Assignment, schema.assignment, )
