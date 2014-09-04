# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Loading of workflows and and set-up and registering of associated adapters.

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.workflows")

#from lxml import etree
from zope import component
from zope.interface import classImplements
from zope.securitypolicy.interfaces import IRolePermissionMap #, IRole
from zope.dottedname.resolve import resolve
from bungeni.models import interfaces
from bungeni.core.workflow import xmlimport
from bungeni.core.workflow.interfaces import IWorkflow, IWorkflowed, \
    IStateController, IWorkflowController
from bungeni.core.workflow.states import StateController, WorkflowController, \
    Workflow, get_object_state_rpm, get_head_object_state_rpm
import bungeni.core.audit #!+
from bungeni.alchemist.utils import inisetattr
from bungeni.utils import naming, misc
from bungeni.capi import capi
from bungeni.alchemist.catalyst import (
    MODEL_MODULE
)


def apply_customization_workflow(type_key, ti):
    """Apply customizations, features as per configuration from a workflow. 
    Must (currently) be run after db setup.
    """
    domain_model, workflow = ti.domain_model, ti.workflow
    assert domain_model and workflow, ti
    # We "mark" the domain class with IWorkflowed, to be able to 
    # register/lookup adapters generically on this single interface.
    #!+directlyImplementedBy? assert not IWorkflowed.implementedBy(domain_model), domain_model
    if not IWorkflowed.implementedBy(domain_model):
        classImplements(domain_model, IWorkflowed)
    # dynamic features from workflow - setup domain/mapping as needed
    for feature in workflow.features:
        feature.setup_model(domain_model)


def register_specific_workflow_adapter(ti):
    # Specific adapter on specific iface per workflow.
    # Workflows are also the factory of own AdaptedWorkflows.
    # Note: cleared by each call to zope.app.testing.placelesssetup.tearDown()
    assert ti.workflow, ti
    assert ti.interface, ti
    # component.provideAdapter(factory, adapts=None, provides=None, name="")
    component.provideAdapter(ti.workflow, (ti.interface,), IWorkflow)

def register_generic_workflow_adapters():
    """Register general and specific worklfow-related adapters.
    
    Note: as the registry is cleared when placelessetup.tearDown() is called,
    this needs to be called independently on each doctest.
    """
    # General adapters on generic IWorkflowed (once for all workflows).
    
    # IRolePermissionMap adapter for IWorkflowed objects
    component.provideAdapter(get_object_state_rpm, 
        (IWorkflowed,), IRolePermissionMap)
    # NOTE: the rpm instance returned by IRolePermissionMap(workflowed) is
    # different for different values of workflowed.status
    
    # IRolePermissionMap adapter for a change of an IWorkflowed object
    component.provideAdapter(get_head_object_state_rpm, 
        (interfaces.IChange,), IRolePermissionMap)
    # NOTE: the rpm instance returned by IRolePermissionMap(change) is
    # different for different values of change.head.status
    
    # !+IPrincipalRoleMap(mr, aug-2011) also migrate principal_role_map from 
    # db to be dynamic and based on workflow definitions. Would need to infer
    # the Roles of a user with respect to the context e.g.owner, or signatory
    # and then check against the permissions required by the current object's
    # state. 
    
    # IStateController
    component.provideAdapter(
        StateController, (IWorkflowed,), IStateController)
    # IWorkflowController
    component.provideAdapter(
        WorkflowController, (IWorkflowed,), IWorkflowController)    


@capi.bungeni_custom_errors
def register_custom_types():
    """Extend TYPE_REGISTRY with the declarations from bungeni_custom/types.xml.
    This is called prior to loading of the workflows for these custom types.
    Returns (type_key, TI) for the newly created TI instance.
    """
    xas, xab = misc.xml_attr_str, misc.xml_attr_bool
    tag_archetype_key_mapping = {
        "doc": "doc",
        "event": "event",
        "group": "group",
        "member": "group_member"
    }
    def parse_elem(type_elem):
        type_key = xas(type_elem, "name")
        workflow_key = xas(type_elem, "workflow")
        descriptor_key = xas(type_elem, "descriptor")
        sys_archetype_key = tag_archetype_key_mapping[type_elem.tag]
        custom_archetype_key = xas(type_elem, "archetype")
        label = xas(type_elem, "label", None)
        container_label = xas(type_elem, "container_label", None)
        return (type_key, sys_archetype_key, custom_archetype_key, 
            workflow_key, descriptor_key, 
            label, container_label)
    
    def enabled_elems(elems):
        for elem in elems:
            if xab(elem, "enabled", default=True):
                yield elem
    
    # load types.xml
    file_path = capi.get_path_for("types.xml")
    etypes = capi.schema.validate_file_rng("types", file_path)
    # register enabled types - ignoring not enabled types
    from bungeni.alchemist import type_info
    
    # custom "event" types (must be loaded prior to custom "doc" types)
    for etype in enabled_elems(etypes.iterchildren("event")):
        type_key, ti = type_info.register_new_custom_type(*parse_elem(etype))
    # custom "doc" types
    for etype in enabled_elems(etypes.iterchildren("doc")):
        type_key, ti = type_info.register_new_custom_type(*parse_elem(etype))
    # group/member types
    for egroup in enabled_elems(etypes.iterchildren("group")):
        group_type_key, ti = type_info.register_new_custom_type(*parse_elem(egroup))
        ti.domain_model.privilege_extent = xas(egroup, "privilege_extent", "group")
        for emember in enabled_elems(egroup.iterchildren("member")):
            type_key, ti = type_info.register_new_custom_type(*parse_elem(emember))
            ti.within_type_key = group_type_key
    
    # SYSTEM WIDE settings (set on class attributes on capi)
    capi.__class__.bicameral = xab(etypes, "bicameral")
    capi.__class__.country_code = xas(etypes, "country_code")
    capi.__class__.legislature_type_key = xas(etypes, "legislature_type")
    capi.__class__.chamber_type_key = xas(etypes, "chamber_type")
    
    # sanity checks
    for tk in (capi.chamber_type_key, capi.legislature_type_key):
        ti = capi.get_type_info(tk) # KeyError
        assert ti.sys_archetype_key == "group", \
            "Value %r specified for %r must be a %r" % (tk, attr, "group")


def load_workflow(type_key, ti):
    """Load (from XML definition), set the workflow instance, and setup (once).
    """
    if ti.workflow_key is None:
        return
    assert ti.workflow is None
    workflow_file_key = ti.workflow_key # workflow file name
    
    # workflow_name -> what becomes workflow.name (and ti.permissions_type_key)
    workflow_name = workflow_file_key 
    if ti.custom and type_key != workflow_file_key:
        workflow_name = type_key         
    # !+ only (non-custom type) "address" wf is multi-used by user_address/group_address
    
    try:
        # retrieve
        ti.workflow = Workflow.get_singleton(workflow_name)
        log.warn("Already Loaded WORKFLOW: %s.xml as %r - %s" % (
            workflow_file_key, workflow_name, ti.workflow))
    except KeyError:
        # load
        ti.workflow = xmlimport.load(workflow_file_key, workflow_name)
        log.info("Loaded WORKFLOW: %s.xml as %r - %s" % (
            workflow_file_key, workflow_name, ti.workflow))
        # debug info
        for state_id, state in ti.workflow.iter_states():
            log.debug("   STATE: %s %s" % (state_id, state))
            for p in state.permissions:
                log.debug("          %s" % (p,))
    
    # setup
    if ti.workflow:
        apply_customization_workflow(type_key, ti)
        register_specific_workflow_adapter(ti)


def retrieve_domain_model(type_key):
    """Infer and retrieve the target domain model class from the type key.
    Raise AttributeError if not defined on model module.
    !+ mv to catalyst.utils?
    """
    return resolve("%s.%s" % (MODEL_MODULE.__name__, naming.model_name(type_key)))

def _setup_all():
    """Do all workflow related setup.
    
    This is the entry point of setup from configuration, with the main other
    participating modules being:
    - alchemist/type_info.py
    - alchemist/model.py
    - ui/descriptor/localization.py
    """
    log.info("adapters._setup_all() ------------------------------------------")
    # cleared by each call to zope.app.testing.placelesssetup.tearDown()
    register_generic_workflow_adapters()
    
    # system and archetypes
    for type_key, ti in capi.iter_type_info():
        # retrieve the domain class and associate domain class with this type
        inisetattr(ti, "domain_model", retrieve_domain_model(type_key))
        # load/get workflow instance (if any) and associate with type
        load_workflow(type_key, ti)
    
    # custom types
    # - first register/update each type in types.xml
    register_custom_types()
    for type_key, ti in capi.iter_type_info(scope="custom"):
        # load/get workflow instance (if any) and associate with type
        load_workflow(type_key, ti)
    
    # check/regenerate zcml directives for workflows - needs to be when and 
    # right-after *all* workflows are loaded (to pre-empt further application 
    # loading with possibly stale permission configuration).
    from bungeni.core.workflow import xmlimport
    xmlimport.zcml_check_regenerate()

# do it (when this module is loaded)
_setup_all()

#

