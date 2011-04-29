#
import datetime
from zope import interface
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile

from bungeni.alchemist import Session
from bungeni.alchemist.model import queryModelDescriptor
from sqlalchemy.orm import eagerload, lazyload
import sqlalchemy.sql.expression as sql

from bungeni.models import domain, schema
from bungeni.core.globalsettings import getCurrentParliamentId
from bungeni.core.dc import IDCDescriptiveProperties

from bungeni.ui.utils import misc, url, debug
from bungeni.ui.cookies import get_date_range
from bungeni.ui.tagged import get_states

class WhatsOnBrowserView(BrowserView):
    __call__ = ViewPageTemplateFile("templates/whatson.pt")
            
    def __init__(self, context, request):
        super(WhatsOnBrowserView, self).__init__(context, request)
        parliament_id = getCurrentParliamentId()
        if parliament_id:
            session = Session()
            parliament = session.query(domain.Parliament).get(parliament_id)
            self.context = parliament
            self.context.__parent__ = context
            self.context.__name__ = ""
        start_date, end_date = get_date_range(request)
        if type(start_date) != datetime.date:
            self.start_date = datetime.date.today()
        else:
            self.start_date = start_date
        if type(end_date) != datetime.date:
            end_date = datetime.date.today() + datetime.timedelta(10)
            self.end_date = datetime.datetime(end_date.year, end_date.month, 
                end_date.day, 23, 59)
        else:
            self.end_date = datetime.datetime(end_date.year, end_date.month, 
                end_date.day, 23, 59)
        self.get_items()
    
    def get_end_date(self): 
        formatter = self.request.locale.dates.getFormatter('date', 'full') 
        return formatter.format(self.end_date)


    def get_start_date(self):
        formatter = self.request.locale.dates.getFormatter('date', 'full') 
        return formatter.format(self.start_date)
        
    def get_sitting_items(self, sitting):
        s_list = []
        if sitting.status in get_states('groupsitting',tagged=['agendaprivate']):
            return s_list
        else:
        # !+DCPROPERTIES(murithi, april-2011) Factor out properties+i18n to DC
            for schedule in sitting.item_schedule:
                descriptor = queryModelDescriptor(schedule.item.__class__)
                s_list.append({
                    'name': IDCDescriptiveProperties(schedule.item).title,
                    'status' : str(misc.get_wf_state(schedule.item))
                    ,
                    'url' : url.set_url_context(('/business/' +
                            schedule.item.type + 's/obj-' + 
                        str(schedule.item.parliamentary_item_id))),
                    'item_type': schedule.item.type,
                    'item_type_title' : (
                        descriptor.display_name if descriptor else
                            schedule.item.type
                    ),
                })
            return s_list
        
    def get_sittings(self):
        formatter = self.request.locale.dates.getFormatter('date', 'full') 
        session = Session()
        query = session.query(domain.GroupSitting).filter(
            sql.and_(
                schema.group_sittings.c.status.in_(get_states('groupsitting',
                    tagged=['public'])
                ),
                sql.between(
                    schema.group_sittings.c.start_date,
                    self.start_date,
                    self.end_date))).order_by(
                        schema.group_sittings.c.start_date).options(
                        eagerload('group'), 
                        #eagerload('sitting_type'),
                        eagerload('item_schedule'), 
                        eagerload('item_schedule.item')
            )
        sittings = query.all()
        day = u''
        day_list = []
        s_dict = {}
        for sitting in sittings:
            sday = formatter.format(sitting.start_date)
            if sday != day:
                s_list = []
                day = sday
                if s_dict:
                    day_list.append(s_dict)
                s_dict = {}
            if sitting.group.type == 'parliament':
                _url = url.set_url_context('/business/sittings/obj-%i' % (
                     sitting.group_sitting_id))
            elif sitting.group.type == 'committee':
                _url = url.set_url_context(
                    '/business/committees/obj-%i/sittings/obj-%i'
                    % (sitting.group.group_id, sitting.group_sitting_id))
            else:
                _url ='#'
            s_list.append({
                'start': sitting.start_date.strftime("%H:%M"),
                'end' : sitting.end_date.strftime("%H:%M"),
                'type' : sitting.group.type,
                'name' : sitting.group.short_name,
                'url' : _url, 
                'items' : self.get_sitting_items(sitting),
                })
            s_dict['day'] = day
            s_dict['sittings'] = s_list
        else:
            if s_dict:
                day_list.append(s_dict)
        return day_list

    def get_items(self):
        session = Session()
        where_clause = sql.and_(
                schema.group_sittings.c.status.in_(get_states(
                                    "groupsitting", tagged=["public"], 
                                    not_tagged=["agendaprivate"], 
                                    conjunction="AND")),
                sql.between(
                    schema.group_sittings.c.start_date,
                    self.start_date,
                    self.end_date))
            
        query = session.query(domain.ItemSchedule).join(
            domain.GroupSitting
            ).filter( 
            where_clause).order_by(schema.group_sittings.c.start_date).options(
                    eagerload('sitting'), eagerload('item'),
                    #eagerload('sitting.sitting_type'),
                    lazyload('item.owner'))
        self.itemschedules = query.all()
                
    def get_items_by_type(self, item_type):
        day = u''
        day_list = []
        s_dict = {}
        formatter = self.request.locale.dates.getFormatter('date', 'full') 
        for schedule in self.itemschedules:
            if type(schedule.item) == item_type:
                sday = formatter.format(schedule.sitting.start_date)
                if sday != day:
                    s_list = []
                    day = sday
                    if s_dict:
                        day_list.append(s_dict)
                    s_dict = {}
                s_list.append({
                    'name': IDCDescriptiveProperties(schedule.item).title,
                    'status' : str(misc.get_wf_state(schedule.item)),
                    'url' : url.set_url_context("/business/%ss/obj-%s" % (
                                        schedule.item.type,
                                        schedule.item.parliamentary_item_id)),
                    'group_type': schedule.sitting.group.type,
                    'group_name' : schedule.sitting.group.short_name
                     })
                s_dict['day'] = day
                s_dict['items'] = s_list
        if s_dict:
            day_list.append(s_dict)
        return day_list
        
    def get_questions(self):
        return self.get_items_by_type(domain.Question)
        
    def get_bills(self):
        return self.get_items_by_type(domain.Bill)
        
    def get_motions(self):
        return self.get_items_by_type(domain.Motion)
        
    def get_tableddocuments(self):
        return self.get_items_by_type(domain.TabledDocument) 

    def get_agendaitems(self):
        return self.get_items_by_type(domain.AgendaItem) 


class WhatsOnPortletBrowserView(WhatsOnBrowserView):
    max_items = 5
    def get_sittings(self):
        return super(WhatsOnPortletBrowserView,
                self).get_sittings()[:self.max_items]
    
    def get_items_by_type(self, item_type):
        return super(WhatsOnPortletBrowserView,
                self).get_items_by_type(item_type)[:self.max_items]


