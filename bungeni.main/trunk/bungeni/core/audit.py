# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Auditing of Changes for Domain Objects

$Id$
"""

from datetime import datetime
from types import StringTypes

from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope import lifecycleevent

from bungeni.core import workflow
from bungeni.alchemist.interfaces import IRelationChange
from bungeni.alchemist import Session
from sqlalchemy import orm

from bungeni.models import schema, domain
from bungeni.models.utils import get_db_user_id
from bungeni.core import interfaces
from bungeni.ui.utils import common

from i18n import _ 


# public handlers

def objectAdded(ob, event):
    auditor = getAuditor(ob)
    auditor.objectAdded(removeSecurityProxy(ob), event)

def objectModified(ob, event):
    auditor = getAuditor(ob)
    if getattr(event, "change_id", None):
        return
    auditor.objectModified(removeSecurityProxy(ob), event)

def objectDeleted(ob, event):
    auditor = getAuditor(ob)
    auditor.objectDeleted(removeSecurityProxy(ob), event)

def objectStateChange(ob, event):
    auditor = getAuditor(ob)
    change_id = auditor.objectStateChanged(removeSecurityProxy(ob), event)
    event.change_id = change_id

def objectNewVersion(ob, event):
    auditor = getAuditor(ob)
    if not getattr(event, "change_id", None):
        change_id = auditor.objectNewVersion(removeSecurityProxy(ob), event)
    else:
        change_id = event.change_id
    event.version.change_id = change_id

def objectRevertedVersion(ob, event):
    # slightly obnoxious hand off between event handlers (objectnewV, objectrevertedV),
    # stuffing onto the event for value passing
    auditor = getAuditor(ob)
    change_id = auditor.objectRevertedVersion(removeSecurityProxy(ob), event)
    event.change_id = change_id

def objectAttachment(ob, event):
    auditor = getAuditor(ob) 
    auditor.objectAttachment(removeSecurityProxy(ob), event)

def objectContained(ob, event):
    auditor = getAuditor(ob) 
    auditor.objectContained(removeSecurityProxy(ob), event)


# internal auditing utilities

def getAuditableParent(obj):
    parent = obj.__parent__
    while parent:
        if  interfaces.IAuditable.providedBy(parent):
            return parent
        else:
            parent = getattr(parent, "__parent__", None)

def getAuditor(ob):
    return globals().get("%sAuditor" %(ob.__class__.__name__))


class AuditorFactory(object):
    
    def __init__(self, change_table, change_object):
        self.change_table = change_table
        self.change_object = change_object
    
    def objectContained(self, object, event):
        self._objectChanged(event.cls, object, event.description)
    
    def objectAttachment(self, object, event):
        self._objectChanged("attachment", object, event.description)
    
    def objectAdded(self, object, event):
        return self._objectChanged("added", object)
    
    def objectModified(self, object, event):
        attrset = []
        for attr in event.descriptions:
            if lifecycleevent.IAttributes.providedBy(attr):
                attrset.extend(
                    [ attr.interface[a].title for a in attr.attributes]
                   )
            elif IRelationChange.providedBy(attr):
                if attr.description:
                    attrset.append(attr.description)
        attrset.append(getattr(object, "note", u""))
        str_attrset = []
        for a in attrset:
            if type(a) in StringTypes:
                str_attrset.append(a)
        description = u", ".join(str_attrset)
        change_data = self._get_change_data()
        if change_data["note"]:
            extras = {"comment": change_data["note"]}
        else:
            extras = None
        return self._objectChanged("modified", object, 
                        description=description,
                        extras=extras,
                        date_active=change_data["date_active"])
    
    def objectStateChanged(self, object, event):
        """
        object: origin domain workflowed object 
        event: bungeni.core.workflow.states.WorkflowTransitionEvent
            .object # origin domain workflowed object 
            .source # souirce state
            .destination # destination state
            .transition # transition
            .comment #
        """
        change_data = self._get_change_data()
        # if note, attach it on object (if object supports such an attribute)
        if change_data["note"]:
            if hasattr(object, "note"):
                object.note = change_data["note"]
        # update object's workflow status date (if supported by object)
        if hasattr(object, "status_date"):
            object.status_date = change_data["date_active"] or datetime.now()
        # as a "base" description, use human readable workflow state title
        wf = workflow.interfaces.IWorkflow(object) # !+ adapters.get_workflow(object)
        description = wf.get_state(event.destination).title
        # extras, that may be used e.g. to elaborate description at runtime
        extras = {
            "source": event.source, 
            "destination": event.destination,
            "transition": event.transition.id,
            "comment": change_data["note"]
        }
        return self._objectChanged("workflow", object, 
                        description=description,
                        extras=extras,
                        date_active=change_data["date_active"])
        # description field is a "building block" for a UI description;
        # extras/notes field becomes interpolation data
    
    def objectDeleted(self, object, event):
        #return self._objectChanged("deleted", object)
        return

    def objectNewVersion(self, object, event):
        """
        object: origin domain workflowed object 
        event: bungeni.core.interfaces.VersionCreated
            .object # origin domain workflowed object 
            .message # title of the version object
            .version # bungeni.models.domain.*Version
            .versioned # bungeni.core.version.Versioned
        """
        # At this point, the new version instance (at event.version) is not yet 
        # persisted to the db (or added to the session!) so its version_id is
        # still None. We force the issue, by adding it to session and flushing.
        session = Session()
        session.add(event.version)
        session.flush()
        # as base description, record a the version object's title
        description = event.message
        # extras, that may be used e.g. to elaborate description at runtime        
        extras = {
            "version_id": event.version.version_id
        }
        return self._objectChanged("new-version", object, description, extras)
        #vkls = getattr(domain, "%sVersion" % (object.__class__.__name__))
        #versions = session.query(vkls
        #            ).filter(vkls.content_id==event.version.content_id
        #            ).order_by(vkls.status_date).all()

    def objectRevertedVersion(self, object, event):
        return self._objectChanged("reverted-version", object,
            description=event.message)
    
    #
    
    def _objectChanged(self, change_kind, object, 
            description="", extras=None, date_active=None):
        """
        description: 
            this is a non-localized string as base description of the log item,
            offers a (building block) for the description of this log item. 
            UI components may use this in any of the following ways:
            - AS IS, optionally localized
            - as a building block for an elaborated description e.g. for 
              generating descriptions that are hyperlinks to an event or 
              version objects
            - ignore it entirely, and generate a custom description via other
              means e.g. from the "notes" extras dict.
        
        extras: !+CHANGE_EXTRAS(mr, dec-2010)
            a python dict, containing "extra" information about the log item, 
            with the "key/value" entries depending on the change "action"; 

            Specific examples, for acttions: 
                workflow: self.objectStateChanged()
                    source
                    destination
                    transition
                    comment
                new-version: self.objectNewVersion()
                    version_id
                modified: self.objectModified()
                    comment
            
            For now, this dict is serialized (using repr(), values are assumed 
            to be simple strings or numbers) as the value of the notes column, 
            for storing in the db--but if and when the big picture of these 
            extra keys is understood clearly then the changes table may be 
            redesigned to accomodate for a selection of these keys as real 
            table columns.                        
        
        date_active:
            the UI for some changes allow the user to manually set the 
            date_active -- this is what should be used as the *effective* date 
            i.e. the date to be used for all intents and purposes other than 
            for data auditing. When not user-modified, the value should be equal 
            to date_audit. 
        """
        oid, otype = self._getKey(object)
        user_id = get_db_user_id()
        assert user_id is not None, _("Participation has no principal")
        session = Session()
        change = self.change_object()
        change.action = change_kind
        change.date_audit = datetime.now()
        if date_active:
            change.date_active = date_active
        else:
            change.date_active = change.date_audit
        change.user_id = user_id
        change.description = description
        change.extras = extras
        change.content_type = otype
        change.origin = object
        session.add(change)
        session.flush()
        return change.change_id
        
    def _getKey(self, ob):
        mapper = orm.object_mapper(ob)
        primary_key = mapper.primary_key_from_instance(ob)[0]
        return primary_key, unicode(ob.__class__.__name__)

    def _get_change_data(self):
        """If request defines change_data, use it, else return a dummy dict.
        """
        try:
            cd = IAnnotations(common.get_request()).get("change_data")
            assert cd is not None, "change_data dict is None."
        except (TypeError, AssertionError):
            # Could not adapt... under testing, the "request" is a 
            # participation that has no IAnnotations.
            cd = {}
        cd.setdefault("note", cd.get("note", ""))
        cd.setdefault("date_active", cd.get("date_active", None))
        return cd


# dedicated auditor instances

BillAuditor = AuditorFactory(
                schema.bill_changes, domain.BillChange)
MotionAuditor = AuditorFactory(
                schema.motion_changes, domain.MotionChange)
QuestionAuditor = AuditorFactory(
                schema.question_changes, domain.QuestionChange)
AgendaItemAuditor =  AuditorFactory(
                schema.agenda_item_changes, domain.AgendaItemChange)
TabledDocumentAuditor =  AuditorFactory(
                schema.tabled_document_changes, domain.TabledDocumentChange)
AttachedFileAuditor =  AuditorFactory(
                schema.attached_file_changes, domain.AttachedFileChange)
GroupSittingAuditor = AuditorFactory(
                schema.group_sitting_changes, domain.GroupSittingChange)
#

