# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni Application - Feature UI handling

$Id$
"""
log = __import__("logging").getLogger("bungeni.feature")


from zope.configuration import xmlconfig
from bungeni.models import domain
from bungeni.capi import capi
from bungeni.utils import naming, misc


ZCML_SLUG = """
<configure xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser"
    xmlns:i18n="http://namespaces.zope.org/i18n"
    i18n_domain="bungeni">
    
    <include package="zope.browsermenu" file="meta.zcml" />
    <include package="zope.browserpage" file="meta.zcml" />
    <include package="zope.viewlet" file="meta.zcml" />

{ui_zcml_decls}

</configure>
"""

UI_ZC_DECLS = []


# utils

def new_container_sub_form_viewlet_cls(type_key, info_container, order):
    """Generate a new viewlet class for this custom container attribute.
    """
    info_container.viewlet_name = \
        container_sub_form_viewlet_cls_name(type_key, info_container)
    import bungeni.ui.forms.viewlets as VIEWLET_MODULE
    cls = type(info_container.viewlet_name, (VIEWLET_MODULE.SubformViewlet,), {
        "sub_attr_name": info_container.container_attr_name,
        "weight": (1 + order) * 10,
    })
    # set on VIEWLET_MODULE
    setattr(VIEWLET_MODULE, info_container.viewlet_name, cls)
    return cls

def container_sub_form_viewlet_cls_name(type_key, info_container):
    return "_".join(["SFV", type_key, info_container.container_attr_name])



def setup_customization_ui():
    """Called from ui.app.on_wsgi_application_created_event -- must be called
    late, at least as long as there other ui zcml directives (always executed 
    very late) that need to have been executed prior to this e.g. 
    creation of specific menus such as "context_actions".
    """
    
    def register_menu_item(type_key, privilege, title, for_, action,
            menu="context_actions", 
            order=10,
            layer="bungeni.ui.interfaces.IBungeniSkin"
        ):
        naming.MSGIDS.add(title) # for i18n extraction
        UI_ZC_DECLS.append(register_menu_item.TMPL.format(**locals()))
    register_menu_item.TMPL = """
            <browser:menuItem menu="{menu}"
                for="{for_}"
                action="{action}"
                title="{title}"
                order="{order}"
                permission="bungeni.{type_key}.{privilege}"
                layer="{layer}"
            />"""
    
    def register_form_view(type_key, privilege, name, for_, class_,
            layer="bungeni.ui.interfaces.IBungeniSkin"
        ):
        UI_ZC_DECLS.append(register_form_view.TMPL.format(**locals()))
    register_form_view.TMPL = """
            <browser:page name="{name}"
                for="{for_}"
                class="{class_}"
                permission="bungeni.{type_key}.{privilege}"
                layer="{layer}"
            />"""
    
    def register_container_viewlet(type_key, name, for_):
        UI_ZC_DECLS.append(register_container_viewlet.TMPL.format(**locals()))    
    register_container_viewlet.TMPL = """
            <browser:viewlet name="bungeni.viewlet.{name}"
                manager="bungeni.ui.forms.interfaces.ISubFormViewletManager"
                for="{for_}"
                class="bungeni.ui.forms.viewlets.{name}"
                permission="zope.Public"
            />"""
    
    def model_title(type_key):
        return naming.split_camel(naming.model_name(type_key))
    
    UI_ZC_DECLS[:] = []
    # we assume that non-custom types have already been set up as needed
    for type_key, ti in capi.iter_type_info(scope="custom"):
        UI_ZC_DECLS.append("""
            
            <!-- {type_key} -->""".format(type_key=type_key))
        
        type_title = model_title(type_key)
        # model interface is defined, but container interface is not yet
        model_interface_qualname = naming.qualname(ti.interface)
        container_interface_qualname = "bungeni.models.interfaces.%s" % (
                naming.container_interface_name(type_key))
        
        # generic forms (independent of any feature)
        # add
        register_form_view(type_key, "Add", "add", container_interface_qualname,
            "bungeni.ui.forms.common.AddForm")
        # api add
        register_form_view(type_key, "Add", "add", container_interface_qualname,
            "bungeni.ui.api.APIAddForm", "bungeni.ui.interfaces.IBungeniAPILayer")
        # view
        register_form_view(type_key, "View", "index", model_interface_qualname,
            "bungeni.ui.forms.common.DisplayForm")
        # api view
        register_form_view(type_key, "View", "index",
                model_interface_qualname,
                "bungeni.ui.api.APIObjectView",
                "bungeni.ui.interfaces.IBungeniAPILayer")
        # edit 
        # !+DiffEditForm prior to r10032, doc-archetyped types were being
        # *declared* to use bungeni.ui.forms.forms.DiffEditForm, but this
        # is not the edit view tht was actually being used!
        #register_form_view(type_key, "Edit", "edit", model_interface_qualname,
        #    "bungeni.ui.forms.common.EditForm")
        if issubclass(ti.domain_model, domain.Group):
            # groups
            register_form_view(type_key, "Edit", "edit",
                model_interface_qualname,
                "bungeni.ui.forms.common.GroupEditForm")
        else:
            register_form_view(type_key, "Edit", "edit",
                model_interface_qualname,
                "bungeni.ui.forms.common.EditForm")
            register_form_view(type_key, "Edit", "edit",
                model_interface_qualname,
                "bungeni.ui.api.APIEditForm",
                "bungeni.ui.interfaces.IBungeniAPILayer")
        # delete
        register_form_view(type_key, "Delete", "delete", model_interface_qualname,
            "bungeni.ui.forms.common.DeleteForm")
        
        # plone content menu (for custom types)
        # !+ doc-types were previously being layered on IWorkspaceOrAdminSectionLayer
        register_menu_item(type_key, "Add", "Add %s..." % (type_title), 
            container_interface_qualname,
            "./add",
            menu="plone_contentmenu",
            layer="bungeni.ui.interfaces.IAdminSectionLayer")
        
        # group        
        if issubclass(ti.domain_model, domain.Group):
            if ti.workflow.has_feature("sitting"):
                # !+CHAMBER_SITTING clarify/regularize for chamber (e.g. can
                # already add an agenda item via workspace menus, etc).
                # add sitting
                register_menu_item("sitting", "Add", "Add %s..." % (model_title("sitting")),
                    model_interface_qualname,
                    "./sittings/add",
                    menu="additems", 
                    order=40,
                    layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer")
                # add agenda_item !+CUSTOM?
                register_menu_item("agenda_item", "Add", "Add %s..." % (model_title("agenda_item")),
                    model_interface_qualname,
                    "./agenda_items/add",
                    menu="additems", 
                    order=41,
                    layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer")
                # group CalendarView
                register_form_view(type_key, "View", "schedule",
                    model_interface_qualname,
                    "bungeni.ui.calendar.browser.CalendarView")

        # member
        if issubclass(ti.domain_model, domain.GroupMember):
            # !+ all were: layer=".interfaces.IWorkspaceOrAdminSectionLayer"
            group_ti = capi.get_type_info(ti.within_type_key)
            group_model_interface_qualname = naming.qualname(group_ti.interface)
            # add
            register_menu_item(type_key, "Add", "Add %s..." % (type_title), 
                group_model_interface_qualname,
                "./%s/add" % (naming.plural(type_key)),
                menu="additems", 
                order=61,
                layer="bungeni.ui.interfaces.IAdminSectionLayer")
        
        # group, member
        if issubclass(ti.domain_model, (domain.Group, domain.GroupMember)):
            # !+ all were: layer=".interfaces.IWorkspaceOrAdminSectionLayer"
            # edit
            register_menu_item(type_key, "Edit", "Edit %s..." % (type_title), 
                model_interface_qualname,
                "edit",
                menu="context_actions", 
                order=10,
                layer="bungeni.ui.interfaces.IAdminSectionLayer")
            # delete
            register_menu_item(type_key, "Delete", "Delete %s..." % (type_title), 
                model_interface_qualname,
                "delete",
                menu="context_actions", 
                order=99,
                layer="bungeni.ui.interfaces.IAdminSectionLayer")
        
        # create/register custom container viewlets
        # !+descriptor/restore.py ti.descriptor_model is None when running this utility
        if ti.descriptor_model:
            for i, ic in enumerate(ti.descriptor_model.info_containers):
                if ic.viewlet:
                    sfv_cls = new_container_sub_form_viewlet_cls(type_key, ic, i)
                    register_container_viewlet(
                        type_key, ic.viewlet_name, model_interface_qualname)
        
        # workspace
        if ti.workflow.has_feature("workspace"):
            log.debug("Setting up UI for feature %r for type %r", "workspace", type_key)
            
            # add menu item
            # !+workspace_feature_add(mr, oct-2012) note that an enabled
            # workspace feature also implies "add" functionality for the type
            first_tab = capi.workspace_tabs[0]
            action = "../../{first_tab}/add_{k}".format(
                first_tab=first_tab, k=type_key)
            register_menu_item(type_key, "Add", type_title, "*", action,
                menu="workspace_add_parliamentary_content", order=7)
            
            # add menu item -> for admin ?!
            # !+ why a duplicated (almost identical) menu item for admin?
            # !+ criteria here is having workspace enabled... but, cirterion 
            # should be simply that of being "parliamentary"? Do we need to 
            # formalize this distinction?
            # !+ need a formal "container attribute" naming convention!
            action = "{k}/add".format(k=naming.plural(type_key)) 
            register_menu_item(type_key, "Add", type_title, "*", action,
                menu="context_add_parliamentary_content", order=7)
            
            # edit menu item
            # !+ edit/delete used to be on layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer"
            title = "Edit {t}".format(t=type_title)
            register_menu_item(type_key, "Edit", title, model_interface_qualname, "edit",
                menu="context_actions", order=10)
            
            # delete menu item
            title = "Delete {t}".format(t=type_title)
            register_menu_item(type_key, "Delete", title, model_interface_qualname, "delete",
                menu="context_actions", order=99)
            
            # add view
            name = "add_{type_key}".format(type_key=type_key)
            register_form_view(type_key, "Add", name,
                "bungeni.core.interfaces.IWorkspaceTab",
                "bungeni.ui.workspace.WorkspaceAddForm")
            # api add
            register_form_view(type_key, "Add", name,
                "bungeni.core.interfaces.IWorkspaceTab",
                "bungeni.ui.api.APIWorkspaceAddForm",
                "bungeni.ui.interfaces.IBungeniAPILayer")
        
        # workspace add titles to strings for i18n
        for ws_tab in capi.workspace_tabs:
            naming.MSGIDS.add(("section_workspace_%s" % ws_tab, ws_tab))
        
        # events
        if ti.workflow.has_feature("event"):
            log.debug("Setting up UI for feature %r for type %r", "event", type_key)
            event_feature = ti.workflow.get_feature("event")
            for event_type_key in event_feature.p.types:
                if capi.has_type_info(event_type_key):
                    container_property_name = naming.plural(event_type_key)
                    # add menu item
                    title = "{t} {e}".format(t=type_title, e=model_title(event_type_key))
                    register_menu_item(event_type_key, "Add", "Add %s" %(title),
                        model_interface_qualname, 
                        "./%s/add" % (container_property_name), 
                        menu="additems", 
                        order=21,
                        layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer")
                else:
                    log.warn("IGNORING feature %r ref to disabled type %r", 
                        "event", event_type_key)
        
        # register other non-workspace menu items for custom types (only once)
        # custom events !+GET_ARCHETYPE
        if issubclass(ti.domain_model, domain.Event):
            # edit menu item
            register_menu_item(type_key, "Edit", "Edit {t}".format(t=type_title),
                model_interface_qualname,
                "edit",
                menu="context_actions",
                order=10,
                layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer")
            # delete menu item
            register_menu_item(type_key, "Delete", "Delete {t}".format(t=type_title),
                model_interface_qualname,
                "delete",
                menu="context_actions",
                order=99,
                layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer")
        
        # address
        if ti.workflow.has_feature("address"):
            log.debug("Setting up UI for feature %r for type %r", "address", type_key)
            if issubclass(ti.domain_model, domain.Group):
                title = "Add {t} Address".format(t=type_title)
                #layer="bungeni.ui.interfaces.IWorkspaceOrAdminSectionLayer"
                # add address in the "add items..." menu
                register_menu_item("address", "Add", title, model_interface_qualname, 
                    "./addresses/add", menu="additems", order=80)
            elif issubclass(ti.domain_model, domain.User):
                # !+ User not a custom type (so should never pass here)
                assert False, "Type %s may not be a custom type" % (ti.domain_model)


def apply_customization_ui():
    """Called from ui.app.on_wsgi_application_created_event -- must be called
    AFTER custom types have been catalysed.
    """
    # combine config string and execute it
    zcml = ZCML_SLUG.format(ui_zcml_decls="".join([ zd for zd in UI_ZC_DECLS ]))
    # log zcml directives to a dedicated file (before executing), for easier debugging
    misc.check_overwrite_file(capi.get_path_for("workflows/.auto/ui.zcml"), 
        '<?xml version="1.0"?>\n<!-- !! AUTO-GENERATED !! DO NOT MODIFY !! -->' + zcml)
    # execute the zcml
    log.debug("Executing UI feature configuration:\n%s" % (zcml))
    xmlconfig.string(zcml)


