from zope import schema, component
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.formlib import form
from bungeni.alchemist import Session
from bungeni.alchemist import catalyst

from bungeni.models import domain, interfaces, utils
from alchemist.ui import content

import common, search
from zope.viewlet import viewlet


class Menu(viewlet.ViewletBase):
    
    template = ViewPageTemplateFile("templates/admin-menu-viewlet.pt")
    
    def render(self):
        return self.template()


class UserFormatter(common.AjaxTableFormatter):
    i = interfaces.IUser
    fields = [ i["login"], i["first_name"], i["last_name"],
        i["email"], i["national_id"],
        schema.TextLine(title=u"Type", __name__="type")
    ]
    def getFields(self):
        return self.fields


class UserListing(BrowserView):
    pass


class GroupFormatter(common.AjaxTableFormatter):
    i = interfaces.IGroup
    fields = [i["short_name"],i["full_name"], i["start_date"], i["end_date"], 
              schema.TextLine(title=u"Type", __name__="type")]
    def getFields(self):
        return self.fields


class GroupListing(common.AjaxContainerListing):
    formatter_factory = GroupFormatter


class UserQueryJSON(search.ConstraintQueryJSON):
    
    def getConstraintQuery(self):
        return self.searcher.query_field("object_kind", "user")
    
    def formatResults(self, results):
        r = []
        for i in results:
            r.append(dict(
                login=i.data.get("login", ("",))[0],
                title=i.data.get("title", ("",))[0],
                email=i.data.get("email", ("",))[0],
                object_type=i.data.get("object_type", ("",))[0]
            ))
        return r
        

class GroupQueryJSON(search.ConstraintQueryJSON):
    def getConstraintQuery(self):
        return self.searcher.query_field("object_kind", domain.Group.__name__)


class Index(BrowserView):
    pass


class Settings(catalyst.EditForm):

    form_fields = form.Fields(interfaces.IBungeniSettings)
        
    def update(self):
        settings = component.getUtility(interfaces.IBungeniSettings)()
        self.adapters = {interfaces.IBungeniSettings : settings}
        super(Settings, self).update()


## class FieldEditColumn(column.FieldEditColumn):
##     def renderCell(self, item, formatter):
##         id = self.makeId(item)
##         request = formatter.request
##         field = self.field
##         if self.bind:
##             field = field.bind(item)
##         widget = component.getMultiAdapter((field, request), IInputWidget)
##         widget.setPrefix(self.prefix + "." + id)
##         if self.widget_extra is not None:
##             widget.extra = self.widget_extra
##         if self.widget_class is not None:
##             widget.cssClass = self.widget_class
##         ignoreStickyValues = getattr(formatter, "ignoreStickyValues", False)
##         if ignoreStickyValues or not widget.hasInput():
##             widget.setRenderedValue(self.get(item))
##         return widget()

    
class UserGroups(BrowserView):
    
    def table(self):
        pass


class UserSettings(catalyst.EditForm):

    form_fields = form.Fields(interfaces.IBungeniUserSettings, interfaces.IUser)
    form_fields = form_fields.omit("user_id", "login", "date_of_death", "status")
    
    def update(self):
        session = Session()
        query = session.query(domain.User).filter(
            domain.User.login == self.request.principal.id)
        results = query.all()
        if len(results) == 1:
            user = results[0]
        else:
            user = None
        settings = interfaces.IBungeniUserSettings(user, None)
        if settings is None:
            raise SyntaxError("User Settings Only For Database Users")
        self.adapters = {interfaces.IBungeniUserSettings : settings,
                          interfaces.IUser : user}
        super(UserSettings, self).update()


