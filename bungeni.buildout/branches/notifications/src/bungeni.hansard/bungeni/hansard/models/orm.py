import sqlalchemy as rdb
from sqlalchemy.orm import mapper, relation, column_property, deferred, backref
from bungeni.models import domain as bungeni_domain
from bungeni.models import schema as bungeni_schema
from bungeni.hansard.models import schema
from bungeni.hansard.models import domain

#Hansard
mapper(domain.Hansard, schema.hansards,
        properties = {
            "items": relation(domain.HansardItem,
                              order_by=schema.hansard_items.c.start_date,
                              primaryjoin=(schema.hansard_items.c.hansard_id ==
                                                schema.hansards.c.hansard_id),),
            "media_paths": relation(domain.HansardMediaPaths,
                                    backref="hansards",
                                    lazy=False,
                                    uselist=False ), 
            "sitting": relation(bungeni_domain.GroupSitting, uselist=False),    
            }
       )

mapper(domain.HansardMediaPaths, schema.hansard_media_paths,)

mapper(domain.HansardItem, schema.hansard_items,  
        inherits=bungeni_domain.ParliamentaryItem,
        polymorphic_on=bungeni_schema.parliamentary_items.c.type,
        polymorphic_identity="hansard_item",  
        )

mapper(domain.Speech, 
        schema.speechs, 
        inherits=domain.HansardItem,
        polymorphic_on=schema.hansard_items.c.item_type,
        polymorphic_identity="hansard_speech",
        properties = { 
                'changes':relation( 
                        domain.SpeechChange, 
                        backref='origin', 
                        cascade="all,delete-orphan", 
                        passive_deletes=False
                        ), 
                'person': relation(bungeni_domain.User,
                            primaryjoin=(schema.speechs.c.person_id ==
                                    bungeni_schema.users.c.user_id),
                                    lazy=False,
                                    uselist=False ),
                } 
        ) 
mapper(domain.SpeechChange, schema.speech_changes ) 
mapper(domain.SpeechVersion, 
        schema.speech_versions, 
        properties= { 
                'change':relation( domain.SpeechChange, uselist=False), 
                'head': relation( domain.Speech, uselist=False) }
       )

mapper(domain.HansardParliamentaryItem, 
        schema.hansard_parliamentary_items, 
        inherits=domain.HansardItem,
        polymorphic_on=schema.hansard_items.c.item_type,
        polymorphic_identity="hansard_parliamentary_item",
        properties = { 
                
                'changes':relation( 
                        domain.HansardParliamentaryItemChange, 
                        backref='origin', 
                        cascade="all,delete-orphan", 
                        passive_deletes=False
                        ), 
                'item':relation(domain.ParliamentaryItem,
                        primaryjoin=(schema.hansard_parliamentary_items. \
                            c.parliamentary_item_id == bungeni_schema.parliamentary_items.c.parliamentary_item_id),
                            lazy=False,
                            uselist=False ),
                } 
        )         
mapper(domain.HansardParliamentaryItemChange, 
                                    schema.hansard_parliamentary_item_changes) 
mapper(domain.HansardParliamentaryItemVersion, 
        schema.hansard_parliamentary_item_versions, 
        properties= { 
                'change':relation(domain.HansardParliamentaryItemChange, uselist=False), 
                'head': relation(domain.HansardParliamentaryItem, uselist=False) }
       )

mapper(domain.Take, schema.takes,
        properties = {
            "editor": relation(bungeni_domain.User,
                                primaryjoin=(schema.takes.c.editor_id ==
                                                bungeni_schema.users.c.user_id),
                                    lazy=False,
                                    uselist=False ), 
            "reader": relation(bungeni_domain.User,
                                primaryjoin=(schema.takes.c.reader_id ==
                                                bungeni_schema.users.c.user_id),
                                    lazy=False,
                                    uselist=False ), 
            "reporter": relation(bungeni_domain.User,
                                primaryjoin=(schema.takes.c.reporter_id ==
                                                bungeni_schema.users.c.user_id),
                                    lazy=False,
                                    uselist=False ), 
        } )
mapper(domain.Assignment, schema.assignments,)


