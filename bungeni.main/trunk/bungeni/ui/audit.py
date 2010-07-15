
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from bungeni.core import audit
from sqlalchemy import orm
from zc.table import batching, column
import sqlalchemy as rdb

from bungeni.ui.i18n import _
from bungeni.ui.utils import date
from bungeni.ui import browser
from bungeni.ui import z3evoque

class ChangeBaseView(browser.BungeniBrowserView):
    """Base view for looking at changes to context.
    """
    
    formatter_factory = batching.Formatter
    
    def __init__(self, context, request):
        super(ChangeBaseView, self).__init__(context, request)
        # table to display the versions history
        formatter = date.getLocaleFormatter(self.request, "dateTime", "short")
        # !+ note this breaks the previous sort-dates-as-strings-hack of 
        # formatting dates, for all locales, as date.strftime("%Y-%m-%d %H:%M")
        # that, when sorted as a string, gives correct results.
        self.columns = [
            column.GetterColumn(title=_(u"action"), 
                    getter=lambda i,f:i["action"]),
            column.GetterColumn(title=_(u"date"), 
                    getter=lambda i,f:formatter.format(i["date"])),
            column.GetterColumn(title=_(u"user"), 
                    getter=lambda i,f:i["user_id"]),
            column.GetterColumn(title=_(u"description"), 
                    getter=lambda i,f:i["description"]),
        ]
    
    def listing(self):
        formatter = self.formatter_factory(self.context, self.request,
                        self.getFeedEntries(),
                        prefix="results",
                        visible_column_names=[ c.name for c in self.columns ],
                        columns=self.columns)
        formatter.cssClasses["table"] = "listing"
        formatter.updateBatching()
        return formatter()
        
    @property
    def _log_table(self):
        auditor = audit.getAuditor(self.context)
        return auditor.change_table
        
    def getFeedEntries(self):
        instance = removeSecurityProxy(self.context)
        mapper = orm.object_mapper(instance)
        
        query = self._log_table.select().where(rdb.and_(
                    self._log_table.c.content_id==rdb.bindparam("content_id"))
                ).order_by(self._log_table.c.change_id.desc())
        
        content_id = mapper.primary_key_from_instance(instance)[0] 
        content_changes = query.execute(content_id=content_id)
        return map(dict, content_changes)

class RSS2(ChangeBaseView):
    """RSS Feed for an object
    """

class ChangeLog(ChangeBaseView):
    """Change Log View for an object
    """
    
    # evoque
    __call__ = z3evoque.PageViewTemplateFile("audit.html#changes")
    
    # zpt
    #__call__ = ViewPageTemplateFile("templates/changes.pt")
    
    _page_title = _("Change Log")
    
    def __init__(self, context, request):
        super(ChangeLog, self).__init__(context, request)
        if hasattr(self.context, "short_name"):
            self._page_title = "%s: %s" % (
                                self._page_title, _(self.context.short_name))

