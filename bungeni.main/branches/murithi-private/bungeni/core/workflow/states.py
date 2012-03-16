# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni Workflow Library

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.workflow.state")

import zope.component
import zope.interface
import zope.securitypolicy.interfaces
import zope.security.management
import zope.security.interfaces
from zope.security.proxy import removeSecurityProxy
from zope.security.checker import CheckerPublic
import zope.event
import zope.lifecycleevent
from bungeni.alchemist import Session
from bungeni.core.workflow import interfaces
from bungeni.utils import error


GRANT, DENY = 1, 0

# we only have 1 or 0 i.e. only Allow or Deny, no Unset.
IntAsSetting = { 
    1: zope.securitypolicy.interfaces.Allow,
    0: zope.securitypolicy.interfaces.Deny
}


def wrapped_condition(condition):
    def test(context):
        if condition is None:
            return True
        try:
            return condition(context)
        except Exception, e:
            raise interfaces.WorkflowConditionError("%s: %s [%s/%s]" % (
                e.__class__.__name__, e, context, condition))
    return test


class Feature(object):
    """Status/settings of an optional feature on a workflowed type.
    """
    def __init__(self, name, enabled=True, note=None, **kws):
        self.name = name
        self.enabled = enabled
        self.note = note
        self.params = kws


class State(object):
    """A workflow state instance. 
    
    For workflowed objects, we infer the permission setting from the permission
    declarations of each workflow state.
    """
    zope.interface.implements(zope.securitypolicy.interfaces.IRolePermissionMap)
    
    def __init__(self, id, title, note, actions, permissions, notifications,
            tags, permissions_from_parent=False, obsolete=False
        ):
        self.id = id # status
        self.title = title
        self.note = note
        self.actions = actions # [callable]
        self.permissions = permissions
        self.notifications = notifications
        self.tags = tags # [str]
        self.permissions_from_parent = permissions_from_parent # bool
        self.obsolete = obsolete # bool
    
    @error.exceptions_as(interfaces.WorkflowStateActionError)
    def execute_actions(self, context):
        """Execute the actions associated with this state.
        """
        assert context.status == self.id, \
            "Context [%s] status [%s] has not been updated to [%s]" % (
                context, context.status, self.id)
        Session().merge(context)
        # actions
        for action in self.actions:
            action(context)
        '''
        # permissions
        rpm = zope.securitypolicy.interfaces.IRolePermissionMap(context)
        for assign, permission, role in self.permissions:
            if assign == GRANT:
               rpm.grantPermissionToRole(permission, role)
            if assign == DENY:
               rpm.denyPermissionToRole(permission, role)
        '''
        # notifications
        for notification in self.notifications:
            # call notification to execute
            notification(context)
    
    # IRolePermissionMap
    #def getPermissionsForRole(self, role_id):
    def getRolesForPermission(self, permission):
        """Generator of (role, setting) tuples for the roles having the 
        permission, as per zope.securitypolicy.interfaces.IRolePermissionMap.
        """
        for setting, p, role in self.permissions:
            if p == permission:
                yield role, IntAsSetting[setting]
    #def getSetting(self, permission, role):
    #    """Return the setting for this principal_id, role_id combination.
    #    """
    #    for setting, p, r in self.permissions:
    #        if p == permission and r == role:
    #            return IntAsSetting[setting]
    #    #return zope.securitypolicy.interfaces.Unset
    #def getRolesAndPermissions(self):
    # /IRolePermissionMap
    #def getSettingAsBoolean(self, permission, role):
    #    """Return getSetting() as a boolean value.
    #    """
    #    return zope.securitypolicy.zopepolicy.SettingAsBoolean[
    #        self.getSetting(permission, role)]


class Transition(object):
    """A workflow transition from source status to destination.
    
    A transition from a *single* source state to a *single* destination state,
    irrespective of how it may be defined e.g. in XML from multiple possible 
    sources to a single destination (this is simply a shorthand for defining
    multiple transitions). 
    
    Each Transition ID is automatically determined from the source and 
    destination states in the following predictable way:
    
        id = "%s-%s" % (source or "", destination)
    
    This is the id to use when calling WorkflowController.fireTransition(id),
    as well as being the HTML id used in generated menu items, etc. 
    """
    
    def __init__(self, title, source, destination,
            grouping_unique_sources=None,
            condition=None,
            trigger=interfaces.MANUAL, 
            permission=CheckerPublic,
            order=0,
            require_confirmation=False,
            note=None,
            **user_data
        ):
        self.title = title
        self.source = source
        self.destination = destination
        self.grouping_unique_sources = grouping_unique_sources
        self._raw_condition = condition # remember unwrapped condition
        self.condition = wrapped_condition(condition)
        self.trigger = trigger
        self.permission = permission
        self.order = order
        self.require_confirmation = require_confirmation
        self.note = note
        self.user_data = user_data
    
    @property
    def id(self):
        # source may be either a valid starus_id or None
        return "%s-%s" % (self.source or "", self.destination)
    
    def __cmp__(self, other):
        return cmp(self.order, other.order)

#

class StateController(object):
    
    zope.interface.implements(interfaces.IStateController)
    
    __slots__ = "context",
    
    def __init__(self, context):
        self.context = context
    
    def get_state(self):
        """Get the workflow.states.State instance for the context's status."""
        return get_object_state(self.context)
    
    def get_status(self):
        return self.context.status
    
    def set_status(self, status):
        source_status = self.get_status()
        if source_status != status:
            self.context.status = status
            # additional actions related to change of workflow status
            self.on_status_change(source_status, status)
        else:
            log.warn("Attempt to reset unchanged status [%s] on item [%s]" % (
                status, self.context))
    
    def on_status_change(self, source, destination):
        state = self.get_state()
        assert state is not None, "May not have a None state" # !+NEEDED?
        state.execute_actions(self.context)


def get_object_state(context):
    """Utility to look up the workflow.states.State singleton instance that 
    corresponds to the context's urrent status.
    
    Implemented as the IWorkflow adaptor for the context--but as may need to 
    be called numerous times per request, note that it is a lightweight and 
    performance-aware adapter -- there is no creation of any adapter instance, 
    just lookup of the object's Workflow instance off which to retrieve 
    existing State instances.
    
    Raises interfaces.InvalidStateError.
    """
    return interfaces.IWorkflow(context).get_state(context.status)


class _NoneStateRPM(State):
    """A dummy State, as fallback IRolePermissionMap, for when Workflow does 
    not define one for a given status; to easier handle error/edge cases of 
    State as IRolePermissionMap, and only methods for defined by this
    interface, e.g. getRolesForPermission(permission), should ever be called!
    """
    # As a minimal concession, we assume it is OK to only grant View access 
    # to the user who actually owns the target instance.
    # !+ROLES(mr, jan-2012) retrieve list of roles dynamically
    permissions = [
        (0, "zope.View", "bungeni.Clerk"),
        (0, "zope.View", "bungeni.Speaker"),
        (1, "zope.View", "bungeni.Owner"),
        (0, "zope.View", "bungeni.Signatory"),
        (0, "zope.View", "bungeni.MP"),
        (0, "zope.View", "bungeni.Minister"),
        (0, "zope.View", "bungeni.Authenticated"),
        (0, "zope.View", "bungeni.Anonymous"),
    ]
    def __init__(self):
        pass
NONE_STATE_RPM = _NoneStateRPM()

def get_object_state_rpm(context):
    """IRolePermissionMap(context) adapter factory. 
    
    Looks up the workflow.states.State singleton instance that is the current
    IRolePermissionMap responsible for the context.
    
    Lighweight and high-performance wrapper on get_object_state(context), 
    to *lookup* (note: no creation of any instance) the workflow.states.State 
    singleton instance.

    On lookup error, returns NONE_STATE_RPM, instead of what would be a 
    zope.component.ComponentLookupError.
    """
    try:
        state = get_object_state(context)
    except interfaces.InvalidStateError, e:
        return NONE_STATE_RPM
    if state.permissions_from_parent:
        # this state delegates permissions to parent, 
        # so just recurse passing parent item instead
        return get_object_state_rpm(context.head)
    return state

def get_head_object_state_rpm(sub_context):
    """IRolePermissionMap(context) adapter factory.
    
    Lighweight and high-performance wrapper on get_object_state(context), 
    to *lookup* (note: no creation of any instance) the workflow.states.State 
    singleton instance for the sub context's head's status.
    
    Note that sub context is NOT workflowed.
    
    On lookup error, returns NONE_STATE_RPM, instead of what would be a 
    zope.component.ComponentLookupError.
    """
    # !+HEAD_DOCUMENT_ITEM(mr, sep-2011) standardize name, "head", "document" 
    # or "item"?
    try:
        return interfaces.IWorkflow(sub_context.head).get_state(sub_context.status)
    except interfaces.InvalidStateError, e:
        return NONE_STATE_RPM
    # !+SUBITEM_CHANGES_PERMISSIONS(mr, jan-2012)

def assert_roles_mix_limitations(perm, roles, wf_name, obj_key, obj_id=""):
    """ Validation utility.
            perm:str, roles:[str]
        for error message:
            wf_name:str, obj_key:either("state", "transition"), obj_id:str
    """
    ROLE_MIX_LIMITATIONS = {
        "bungeni.Authenticated": ["bungeni.Anonymous"],
    }
    for mix_limited_role in ROLE_MIX_LIMITATIONS:
        if mix_limited_role in roles:
            _mixed_roles = roles[:]
            _mixed_roles.remove(mix_limited_role)
            for ok_role in ROLE_MIX_LIMITATIONS[mix_limited_role]:
                if ok_role in _mixed_roles:
                    _mixed_roles.remove(ok_role)
            assert not bool(_mixed_roles), "Workflow [%s] %s [%s] " \
                "mixes disallowed roles %s with role [%s] for " \
                "permission [%s]" % (
                    wf_name, obj_key, obj_id, roles, mix_limited_role, perm)


class Workflow(object):
    """A Workflow instance for a specific document type, defining the possible 
    states a document may have and the allowed transitions between them.
    The initial state of the workflowed document is always None.
    """
    zope.interface.implements(interfaces.IWorkflow)
    
    initial_state = None
    
    def __init__(self, name, features, tags, states, transitions, note=None):
        self.name = name
        self.features = features
        self.tags = tags # [str]
        self.note = note
        self._states_by_id = {} # {id: State}
        self._transitions_by_id = {} # {id: Transition}
        self._transitions_by_source = {} # {source: [Transition]}
        self._transitions_by_destination = {} # {destination: [Transition]}
        self._transitions_by_grouping_unique_sources = {} # {grouping: [Transition]}
        self._permission_role_pairs = None # set([ (permission, role) ])
        self.refresh(states, transitions)
    
    def refresh(self, states, transitions):
        sbyid = self._states_by_id
        sbyid.clear()
        tbyid = self._transitions_by_id
        tbyid.clear()
        tbys = self._transitions_by_source
        tbys.clear()
        tbyd = self._transitions_by_destination
        tbyd.clear()
        tbygus = self._transitions_by_grouping_unique_sources
        tbygus.clear()
        # states
        tbys[self.initial_state] = [] # special case source: initial state
        for s in states:
            sbyid[s.id] = s
            tbys[s.id] = []
            tbyd[s.id] = []
        # transitions
        for t in transitions:
            tid = t.id
            assert tid not in tbyid, \
                "Workflow [%s] duplicates transition [%s]" % (self.name, tid)
            tbyid[tid] = t
            tbys[t.source].append(t)
            tbyd[t.destination].append(t)
            tbygus.setdefault(t.grouping_unique_sources, []).append(t)
        # integrity
        self.validate()
    
    @error.exceptions_as(interfaces.InvalidWorkflow, False)
    def validate(self):
        
        assert len(self.tags) == len(set(self.tags)), \
            "Workflow [%s] duplicates tags: %s" % (self.name, self.tags)
        
        states = self._states_by_id.values()
        # at least one state
        assert len(states), "Workflow [%s] defines no states" % (self.name)
        # every state must explicitly set the same set of permissions
        # prs: set of all (permission, role) pairs assigned in a state
        self._permission_role_pairs = prs = set([ 
            (p[1], p[2]) for p in states[0].permissions ])
        num_prs = len(prs)
        for s in states:
            if s.permissions_from_parent:
                assert not len(s.permissions), "Workflow state [%s -> %s] " \
                    "with permissions_from_parent may not specify any own " \
                    "permissions" % (self.name, s.id)
                continue
            assert len(s.permissions) == num_prs, \
                "Workflow state [%s -> %s] does not explicitly set same " \
                "permissions used across other states... " \
                "\nTHIS:\n  %s\nOTHER:\n  %s" % (self.name, s.id, 
                    "\n  ".join([str(p) for p in s.permissions]),
                    "\n  ".join([str(p) for p in states[0].permissions])
                )
            _permission_role_mixes = {}
            for p in s.permissions:
                perm, role = p[1], p[2]
                # for each perm, build list of roles it is set to
                _permission_role_mixes.setdefault(perm, []).append(role)
                assert (perm, role) in prs, \
                    "Workflow state [%s -> %s] defines an unexpected " \
                    "permission: %s" % (self.name, s.id, p)
            for perm, roles in _permission_role_mixes.items():
                # ensure no duplicates (also checked when reading xml)
                assert len(roles) == len(set(roles)), "Workflow [%s] " \
                    "state [%s] duplicates role [%s] assignment for " \
                    " permission [%s]" % (
                        self.name, s.id, roles, perm)
                # assert roles mix limitations for state permissions
                assert_roles_mix_limitations(perm, roles, self.name, "state", s.id)
            # tags
            _undeclared_tags = [ tag for tag in s.tags if tag not in self.tags ]
            assert not _undeclared_tags, \
                "Workflow [%s] State [%s] uses undeclared tags: %s" % (
                    self.name, s.id, _undeclared_tags)
            assert len(s.tags) == len(set(s.tags)), \
                "Workflow [%s] State [%s] duplicates tags: %s" % (
                    self.name, s.id, s.tags)
        
        # assert roles mix limitations for transitions
        for t in self._transitions_by_id.values():
            roles = t.user_data.get("_roles", [])
            assert_roles_mix_limitations(t.permission, roles, self.name, "transition", t.id)
        
        # ensure that every active state is reachable, 
        # and that every obsolete state is NOT reachable
        tbyd = self._transitions_by_destination
        for dest_id, sources in tbyd.items():
            log.debug("Workflow [%s] sources %s -> destination [%s]" % (
                self.name, [t.source for t in sources], dest_id))
            if self.get_state(dest_id).obsolete:
                assert not sources, \
                    "Reachable obsolete state [%s] in Workflow [%s]" % (
                        dest_id, self.name)
            else:
                assert sources, \
                    "Unreachable state [%s] in Workflow [%s]" % (
                        dest_id, self.name)
        # inter-transition validation
        # grouping_unique_sources - used to semantically connect multiple 
        # transitions and constrain that accumulative sources are unique
        for grouping, ts in self._transitions_by_grouping_unique_sources.items():
            if grouping is not None:
                all_sources = [ t.source for t in ts ]
                assert len(all_sources)==len(set(all_sources)), "Duplicate " \
                    "sources in grouped transitions [%s] in workflow [%s]" % (
                        grouping, self.name)
    
    def has_feature(self, name):
        """Does this workflow enable the named feature?
        """
        for f in self.features:
            if f.name == name:
                return f.enabled
        return False
    
    @property
    def states(self):
        """ () -> { status: State } """
        log.warn("DEPRECATED [%s] Workflow.states, " \
            "use Workflow.get_state(status) instead" % (self.name))
        return self._states_by_id
    
    def get_state(self, state_id):
        """Get State instance for state_id.
        Must raise interfaces.InvalidStateError if no such State.
        """
        try:
            return self._states_by_id[state_id]
        except KeyError:
            raise interfaces.InvalidStateError(
                "Workflow [%s] has no such State [%s]" % (self.name, state_id))
    
    def get_state_ids(self, tagged=[], not_tagged=[], keys=[], conjunction="OR",
            restrict=True, # workflow must define all specified tags/keys
            _EMPTY_SET=set() # re-usable empty set value
        ):
        """Get the list of matching state ids in workflow.
        
        tagged: matches all states tagged with ANY tag in in this list
        not_tagged: matches all states tagged with NONE of these tags
        keys: matches all states explictly named by key here; only keys for
            which a state is actually defined are retained
        conjunction:
            "OR": matches any state that is matched by ANY criteria above
            "AND": matches any state that is matched by ALL criteria above
        restrict: when True (default) all states and keys specified MUST 
            actually be used by the workflow.
        """
        _tagged = _not_tagged = _keys = _EMPTY_SET # matching state ids
        if tagged:
            wf_tagged = [ t for t in tagged if t in self.tags ]
            if restrict:
                assert wf_tagged==tagged
            # for tagged, we only need to consider known tags
            _tagged = set()
            if wf_tagged:
                for state in self._states_by_id.values():
                    for t in wf_tagged:
                        if t in state.tags:
                            _tagged.add(state.id)
                            break
        elif not_tagged:
            if restrict:
                wf_not_tagged = [ t for t in not_tagged if t in self.tags ]
                assert wf_not_tagged==not_tagged
            # for not_tagged, we must also consider all unknown tags
            _not_tagged = set(self._states_by_id.keys())
            for state in self._states_by_id.values():
                for t in not_tagged:
                    if t in state.tags:
                        _not_tagged.remove(state.id)
                        break
        elif keys: # state_ids
            wf_keys = [ k for k in keys if k in self._states_by_id ]
            if restrict:
                assert wf_keys==keys
            # we may only return valid state ids
            _keys = set(wf_keys)
        else:
            # make case of get_state_ids(conjunction="OR") return all state ids
            _not_tagged = set(self._states_by_id.keys())
        # combine
        assert conjunction in ("OR", "AND"), "Not supported."
        if conjunction=="OR":
            return list(_tagged.union(_not_tagged).union(_keys))
        elif conjunction=="AND":
            return list(_tagged.intersection(_not_tagged).union(_keys))
    
    
    @error.exceptions_as(interfaces.InvalidTransitionError)
    def get_transition(self, transition_id):
        return self._transitions_by_id[transition_id]
    
    # !+ get_transitions_to(destination) ? 
    @error.exceptions_as(interfaces.InvalidStateError)
    def get_transitions_from(self, source):
        return sorted(self._transitions_by_source[source])
    
    def __call__(self, context):
        """A Workflow instance is itself the "singleton factory" of itself.
        Called to adapt IWorkflow(context) -- the "adaptation" concept implied
        by this is simply a lookup, on the context's class/interface, for the 
        workflow instance that was registered for that class/interface.
        """
        return self


class WorkflowController(object):
    
    zope.interface.implements(interfaces.IWorkflowController)
        
    def __init__(self, context):
        # assume context is trusted... 
        # and unlitter all actions/conditions of calls to removeSecurityProxy
        self.context = removeSecurityProxy(context)
        self._state_controller = None # cache for state_controller instance
    
    @property
    def state_controller(self):
        if self._state_controller is None:
            self._state_controller = interfaces.IStateController(self.context)
        return self._state_controller
    
    @property
    def workflow(self):
        """ () -> bungeni.core.workflow.states.Workflow """
        return interfaces.IWorkflow(self.context)
    
    def _get_checkPermission(self):
        return zope.security.management.getInteraction().checkPermission
    
    def _check(self, transition, check_security):
        """Check whether we may execute this workflow transition.
        """
        if check_security:
            checkPermission = self._get_checkPermission()
            if not checkPermission(transition.permission, self.context):
                raise zope.security.interfaces.Unauthorized(self.context,
                    "transition: %s" % transition.id, 
                    transition.permission)
        # now make sure transition can still work in this context
        transition.condition(self.context) # raises WorkflowConditionError
    
    # !+ RENAME
    def fireTransition(self, transition_id, comment=None, check_security=True):
        if not (comment is None and check_security is True):
            log.warn("%s.fireTransition(%s, comment=%s, check_security=%s)" % (
                self, transition_id, comment, check_security))
        # raises InvalidTransitionError if id is invalid for current state
        transition = self.workflow.get_transition(transition_id)
        self._check(transition, check_security)
        # change status of context or new object
        self.state_controller.set_status(transition.destination)
        # notify wf event observers
        wte = WorkflowTransitionEvent(self.context, 
            transition.source, transition.destination, transition, comment)
        zope.event.notify(wte)
        # send modified event for original or new object
        ome = zope.lifecycleevent.ObjectModifiedEvent(self.context)
        # !+ORIGINATOR(mr, feb-2012) better to simply not fire a 2nd event?
        ome.originator = wte # !+ could maybe use OME(o, *descriptions)
        zope.event.notify(ome)
    
    def fireTransitionToward(self, state, comment=None, check_security=True):
        transition_ids = self.getFireableTransitionIdsToward(state)
        if not transition_ids:
            raise interfaces.NoTransitionAvailableError
        if len(transition_ids) != 1:
            raise interfaces.AmbiguousTransitionError
        return self.fireTransition(transition_ids[0], comment, check_security)
    
    def fireAutomatic(self):
        # we take the first automatic transitions that passes condition (if any)
        for transition in self._get_transitions(interfaces.AUTOMATIC, True):
            # automatic transitions are not security-checked--assuming proviso
            # that fireAutomatic() is never called as a user action 
            # *directly*, but it is rather the logical consequence of handling 
            # some other direct user action (for which the user would 
            # presumabley have the necessary privilege) e.g. transiting an 
            # item to draft is done automatically when the user creates the 
            # item (assumes of course the privilege of creating the item).
            # 
            # Automatic transitions may still be fired manually, but then 
            # otehr details also have to be handled manually e.g. not checking 
            # the security and checking the condition.
            self.fireTransition(transition.id, comment=None, 
                check_security=False)
    
    def getFireableTransitionIdsToward(self, state):
        workflow = self.workflow
        result = []
        for transition_id in self.getFireableTransitionIds():
            transition = workflow.get_transition(transition_id)
            if transition.destination == state:
                result.append(transition_id)
        return result
    
    def getFireableTransitionIds(self):
        return self.getManualTransitionIds() + self.getSystemTransitionIds()
    
    def getManualTransitionIds(self):
        checkPermission = self._get_checkPermission()
        return [ transition.id 
            for transition in self._get_transitions(interfaces.MANUAL, True)
            if checkPermission(transition.permission, self.context) ]
    
    def getSystemTransitionIds(self):
        # ignore permission checks
        return [ transition.id 
            for transition in self._get_transitions(interfaces.SYSTEM, False) ]
    # !+ /RENAME
    
    def _get_transitions(self, trigger_ifilter=None, conditional=False):
        """Retrieve all possible transitions from current status.
        If trigger_ifilter is not None, filter on trigger interface.
        If conditional, then only transitions that pass the condition.
        """
        transitions = self.workflow.get_transitions_from(
            self.state_controller.get_status())
        # now filter these transitions to retrieve all possible
        # transitions in this context, and return their ids
        return [ transition for transition in transitions
            if ((trigger_ifilter is None or 
                    transition.trigger == trigger_ifilter) and
                (not conditional or transition.condition(self.context))) ]


class WorkflowTransitionEvent(zope.component.interfaces.ObjectEvent):
    """The generic transition event, systematically fired at end of EVERY
    transition.
    """
    zope.interface.implements(interfaces.IWorkflowTransitionEvent)
    
    def __init__(self, object, source, destination, transition, comment):
        super(WorkflowTransitionEvent, self).__init__(object)
        self.source = source
        self.destination = destination
        self.transition = transition
        self.comment = comment

