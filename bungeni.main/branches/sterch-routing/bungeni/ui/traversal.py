#from zope.component import getUtility
from zope.container.traversal import ContainerTraverser
from zope.interface import alsoProvides
#import re
from bungeni.core.content import AkomaNtosoSection, Section
from zope.security.proxy import removeSecurityProxy

from zope.dottedname import resolve
from bungeni.alchemist import Session
from bungeni.models.domain import ParliamentaryItem, Bill
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.security.checker import ProxyFactory
from zope.app.component.hooks import getSite
from zope.interface.declarations import alsoProvides
import datetime, traceback, sys
from sqlalchemy import extract
        

class SiteTraverser(ContainerTraverser):
    """ Custom traverser for special 'bungeni' section
    """

    def __init__(self, container, request):
        self.session = Session()
        super(SiteTraverser, self).__init__(container, request)

    def publishTraverse(self, request, name):
        
        # last section, retrieve object
        if name == "main":
            try:
                object = self.get_query(self.context.type, self.context.id, self.context.date, self.context.lang).one()
                object.__parent__ = self.context
                #return getMultiAdapter((object, request), name='feed.akomantoso')
                return object
            except:
                traceback.print_exception(*sys.exc_info())

        try:
            context = AkomaNtosoSection(
                title=name,
                description=name,
                default_name=name,
            )
            
            self.context[name] = context
            context.id = self.context.id 
            context.date = self.context.date 
            context.lang = self.context.lang 
            context.type = self.context.type
        except:
            traceback.print_exception(*sys.exc_info())

        # for now should always be "ke" 
        if name == 'ke':
            return context
        # getting content type
        if not context.type:
            context.type = name
            return context
        # getting date
        if not context.date:
            context.date = name
            return context
        # getting registry number     
        if not context.id:
            context.id = name
            return context
        # getting language   
        if not context.lang:
            context.lang = name[:-1]
            return context

        return super(SiteTraverser, self).publishTraverse(request, name)
    
    def get_query(self, content_type, id, date, lang):
        d = date.split('-')
        date = datetime.date(int(d[0]), int(d[1]), int(d[2]))
        
        if content_type == "bill":
            return self.session.query(Bill).filter(Bill.registry_number==id).\
                                            filter(Bill.publication_date==date).\
                                            filter(Bill.language==lang)
        return self.session.query(ParliamentaryItem).filter(ParliamentaryItem.registry_number==id).\
                                                     filter(ParliamentaryItem.type==content_type).\
                                                     filter(ParliamentaryItem.language==lang).\
                                                     filter(extract('year',ParliamentaryItem.status_date)==date.year).\
                                                     filter(extract('month',ParliamentaryItem.status_date)==date.month).\
                                                     filter(extract('day',ParliamentaryItem.status_date)==date.day)