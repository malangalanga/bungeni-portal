from sqlalchemy.sql.expression import and_
from zope.component import getUtility
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleMap
from zope.app.security.settings import Allow
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zc.table import column
from zope import formlib

from bungeni.core.dc import IDCDescriptiveProperties
from bungeni.ui.browser import BungeniBrowserView
from bungeni.ui.i18n import _
from bungeni.ui.table import TableFormatter
from bungeni.ui import forms
from bungeni.ui.utils import url, common
from bungeni.utils.capi import capi
from bungeni.alchemist import Session
from bungeni.models import domain, utils
from bungeni.models.interfaces import ISubRoleAnnotations


class AssignmentView(BungeniBrowserView):
    """View for object assignments
    """
    disabled = True
    render = ViewPageTemplateFile("templates/assignment-view.pt")

    def __init__(self, context, request):
        self._assignable_roles = []
        self.principal = utils.get_principal()
        self.context_roles = common.get_context_roles(
            context, self.principal)
        self.context = removeSecurityProxy(context)
        self.prm = IPrincipalRoleMap(self.context)
        super(AssignmentView, self).__init__(context, request)

    def get_object_type_info(self):
        return capi.get_type_info(self.context.__class__)

    def assignable_roles(self):
        if self._assignable_roles:
            return self._assignable_roles
        ti = self.get_object_type_info()
        workflow = ti.workflow
        #the assigner roles that this user has
        assigner_roles = []
        #all the assigner roles that are in the workflow config
        config_assigner_roles = []
        assignable_roles = []
        config_assignable_roles = []
        if workflow.has_feature("assignment"):
            feature = None
            for f in workflow.features:
                if f.name == "assignment":
                    feature = f
            if feature:
                config_assigner_roles = feature.params[
                    "assigner_roles"].split()
                for role in config_assigner_roles:
                    if role in self.context_roles:
                        assigner_roles.append(role)
                config_assignable_roles = feature.params[
                    "assignable_roles"].split()
                for assigner_role in assigner_roles:
                    assigner_role_annt = ISubRoleAnnotations(
                        getUtility(IRole, role))
                    if assigner_role_annt.is_sub_role:
                        #find other sub_roles with the same parent
                        for c_assignable_role in config_assignable_roles:
                            c_assignable_role_annt = ISubRoleAnnotations(
                                getUtility(IRole, c_assignable_role))
                            if (c_assignable_role_annt.parent ==
                                assigner_role_annt.parent):
                                assignable_roles.append(c_assignable_role)
                    else:
                        for c_assignable_role in config_assignable_roles:
                            if (c_assignable_role in
                                assigner_role_annt.sub_roles):
                                assignable_roles.append(c_assignable_role)
        self._assignable_roles = assignable_roles
        return self._assignable_roles

    def get_users(self, role_id):
        session = Session()
        gmrs = session.query(domain.GroupMembershipRole).filter(and_(
            domain.GroupMembershipRole.role_id == role_id,
            domain.GroupMembershipRole.is_global == False)).all()
        return [gmr.member.user for gmr in gmrs]

    @property
    def columns(self):
        return [
            column.GetterColumn(
                title=_("user name"),
                getter=lambda i, f: i.get("title")
            ),
            column.GetterColumn(
                title=_("assigned"),
                getter=lambda i, f: i,
                cell_formatter=lambda g, i, f: \
                    '<input type="checkbox" name="%s" %s %s/>' % (
                        i["name"],
                        i["is_assigned"] and ' checked="checked"' or "",
                        self.disabled and ' disabled="disabled"' or "")
                )
            ]

    @property
    def checkbox_prefix(self):
        return "assignment_users"

    def make_id(self, role_id, user_login_id):
        return ".".join(
            (self.checkbox_prefix, role_id, user_login_id))

    def user_is_assigned(self, user_login, role_id):
        if self.prm.getSetting(role_id, user_login) == Allow:
            return True
        return False

    def role_listing(self, role_id):
        listing = []
        for user in self.get_users(role_id):
            data = {}
            data["title"] = IDCDescriptiveProperties(user).title
            data["name"] = self.make_id(user.login, role_id)
            data["is_assigned"] = self.user_is_assigned(user.login, role_id)
            listing.append(data)
        formatter = TableFormatter(
            self.context, self.request, listing, prefix="assignment",
            columns=self.columns)
        formatter.updateBatching()
        return formatter()

    def update(self):
        self.tables = []
        for role_id in self.assignable_roles():
            self.tables.append(
                {"title": getUtility(IRole, role_id).title,
                 "table": self.role_listing(role_id)})

    def __call__(self):
        self.update()
        return self.render()


class AssignmentEditView(AssignmentView, forms.common.BaseForm):
    disabled = False
    form_fields = []

    render = ViewPageTemplateFile("templates/assignment-edit.pt")

    def update(self):
        AssignmentView.update(self)
        forms.common.BaseForm.update(self)

    def get_selected(self):
        selected = [
            (k[len(self.checkbox_prefix) + 1:].split(".")[0].decode("base64"),
            k[len(self.checkbox_prefix) + 1:].split(".")[1].decode("base64"))
            for k in self.request.form.keys()
            if k.startswith(self.checkbox_prefix) and self.request.form.get(k)
        ]
        return selected

    def process_assignment(self):
        print "################", self.request.form.keys()
        for role_id in self.assignable_roles():
            for user in self.get_users(role_id):
                key = self.make_id(user.login, role_id)
                print "XXXXXXXXXXXXXXXXX", key
                if key in self.request.form.keys():
                    print "XXXXXXXXXXXXXXXXXX\nXXXXX\nXXXXX\nXXXXX"
                    self.prm.assignRoleToPrincipal(role_id, user.login)
                else:
                    self.prm.unsetRoleForPrincipal(role_id, user.login)

    @formlib.form.action(label=_("Save"), name="save")
    def handle_save(self, action, data):
        self.process_assignment()
        next_url = url.absoluteURL(self.context, self.request)
        self.request.response.redirect(next_url)

    @formlib.form.action(label=_("Cancel"), name="")
    def handle_cancel(self, action, data):
        next_url = url.absoluteURL(self.context, self.request)
        self.request.response.redirect(next_url)
