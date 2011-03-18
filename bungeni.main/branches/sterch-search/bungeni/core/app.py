# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""The Bungeni Application 

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.app")

from zope.interface import implements
from zope.interface import implementedBy
from zope.component import provideAdapter

from zope.app.component import site
from zope.app.container.sample import SampleContainer
from zope.location.interfaces import ILocation

from ore.wsgiapp.app import Application

from bungeni.models import domain
from bungeni.models import interfaces as model_interfaces

from bungeni.core import interfaces
from bungeni.core import location
from bungeni.core.content import Section, AdminSection
from bungeni.core.content import QueryContent
from bungeni.core.i18n import _
from bungeni.models.utils import get_current_parliament
from bungeni.models.utils import container_getter
from bungeni.ui.utils import url, common


def onWSGIApplicationCreatedEvent(application, event):
    """Subscriber to the ore.wsgiapp.interfaces.IWSGIApplicationCreatedEvent."""
    initializer = model_interfaces.IBungeniSetup(application)
    initializer.setUp()
    from zope.app.appsetup.appsetup import getConfigContext
    log.debug("onWSGIApplicationCreatedEvent: _features: %s" % (
                                        getConfigContext()._features))

class BungeniApp(Application):
    implements(model_interfaces.IBungeniApplication)
#!CRUFT (miano, nov-2010) possible cruft
#class BungeniAdmin(SampleContainer):
#    implements(model_interfaces.IBungeniAdmin )



class AppSetup(object):
    
    implements(model_interfaces.IBungeniSetup)
    
    def __init__(self, context):
        self.context = context
    
    def setUp(self):
        
        import index
        # ensure indexing facilities are setup(lazy)
        index.setupFieldDefinitions(index.indexer)
        index.reset_index()
        
        sm = site.LocalSiteManager(self.context)
        self.context.setSiteManager(sm)
        
        from bungeni.ui import z3evoque
        z3evoque.set_get_gettext()
        z3evoque.setup_evoque()
        z3evoque.domain.set_on_globals("devmode", common.has_feature("devmode"))
        z3evoque.domain.set_on_globals("absoluteURL", url.absoluteURL)
        z3evoque.domain.set_on_globals("get_section_name", url.get_section_name)
        
        # !+ where is the view name for the app root (slash) set?
        
        # CONVENTION: the action of each site top-section is made to point 
        # directly the primary sub-section (the INDEX) that it contains.
        # EXCEPTION: the "/", when logged in, is redirected to "/workspace/pi"
        
        # top-level sections
        from bungeni.ui.workspace import workspace_resolver
        workspace = self.context["workspace"] = Section(
            title=_(u"Workspace"),
            description=_(u"Current parliamentary activity"),
            default_name="workspace-index",
            publishTraverseResolver=workspace_resolver
        )
        workspace["scheduling"] = Section(
            title=_(u"Scheduling"),
            description=_(u"Scheduling"),
            default_name="scheduling",
            marker = interfaces.IWorkspaceScheduling,
        )
        workspace["scheduling"]["committees"] = QueryContent(
            container_getter(get_current_parliament, 'committees'),
            title=_(u"Committees"),
            marker=interfaces.ICommitteeAddContext,
            description=_(u"Committee schedules"))
        workspace["scheduling"]["sittings"] = QueryContent(
            container_getter(get_current_parliament, 'sittings'),
            title=_(u"Sittings"),
            description=_(u"Plenary Sittings"))
        # Proof-of-concept: support for selective inclusion in breadcrumb trail:
        # a view marked with an attribute __crumb__=False is NOT included in 
        # the breadcrumb trail (see ui/viewlets/navigation.py)
        #self.context["workspace"].__crumb__ = False
        business = self.context["business"] = Section(
            title=_(u"Business"),
            description=_(u"Daily operations of the parliament"),
            default_name="business-index")
        members = self.context["members"] = Section(
            title=_(u"Members"),
            description=_(u"Records on members of parliament"),
            default_name="members-index")
        archive = self.context["archive"] = Section(
            title=_(u"Archive"),
            description=_(u"Parliament records and documents"),
            default_name="archive-index")
            
        #!+SECURITY(miano. nov-2010) Admin section now uses AdminSection
        # container that is identical to Section, only difference is that
        # traversing though it requires zope.ManageSite permission as defined
        # in core/configure.zcml
            
        admin = self.context["admin"] = AdminSection(
            title=_(u"Administration"),
            description=_(u"Administer bungeni settings"),
            default_name="admin-index",
            marker=model_interfaces.IBungeniAdmin)
        
        # business section
        business["whats-on"] = Section(
            title=_(u"What's on"),
            description=_(u"Current parliamentary activity"),
            default_name="whats-on")

        business[u"committees"] = QueryContent(
            container_getter(get_current_parliament, 'committees'),
            title=_(u"Committees"),
            marker=interfaces.ICommitteeAddContext,
            description=_(u"View committees created by the current parliament"))
        
        business[u"bills"] = QueryContent(
            container_getter(get_current_parliament, 'bills'),
            title=_(u"Bills"),
            marker=interfaces.IBillAddContext,
            description=_(u"View bills issued by the current parliament"))

        business[u"questions"] = QueryContent(
            container_getter(get_current_parliament, 'questions'),
            title=_(u"Questions"),
            marker=interfaces.IQuestionAddContext,
            description=_(u"View questions issued by the current parliament"))

        business[u"motions"] = QueryContent(
            container_getter(get_current_parliament, 'motions'),
            title=_(u"Motions"),
            marker=interfaces.IMotionAddContext,
            description=_(u"View motions issued by the current parliament"))


        business[u"tableddocuments"] = QueryContent(
            container_getter(get_current_parliament, 'tableddocuments'),
            title=_(u"Tabled documents"),
            marker=interfaces.ITabledDocumentAddContext,
            description=_(u"View the tabled documents of the current parliament"))

        business[u"agendaitems"] = QueryContent(
            container_getter(get_current_parliament, 'agendaitems'),
            title=_(u"Agenda items"),
            marker=interfaces.IAgendaItemAddContext,
            description=_(u"View the agenda items of the current parliament"))

       # sessions = business[u"sessions"] = QueryContent(
       #     container_getter(get_current_parliament, 'sessions'),
       #     title=_(u"Sessions"),
       #     marker=interfaces.ISessionAddContext,
       #     description=_(u"View the sessions of the current parliament."))

        business[u"sittings"] = QueryContent(
            container_getter(get_current_parliament, 'sittings'),
            title=_(u"Sittings"),
            description=_(u"View the sittings of the current parliament"))
            
        #Parliamentary reports
        business[u"preports"] = QueryContent(
            container_getter(get_current_parliament, 'preports'),
            title=_(u"Publications"),
            marker=interfaces.IReportAddContext,
            description=_(u"View Agenda and Minutes reports of the current parliament"))
        
        
        # members section
        members[u"current"] = QueryContent(
            container_getter(get_current_parliament, 'parliamentmembers'),
            title=_(u"Current"),
            description=_(u"View current parliament members (MPs)"))

        members[u"political-groups"] = QueryContent(
            container_getter(get_current_parliament, 'politicalgroups'),
            title=_(u"Political groups"),
            description=_(u"View current political groups"))

        # archive
        records = archive[u"browse"] = Section(
            title=_(u"Browse"),
            description=_(u"Current and historical records"),
            default_name="browse-archive")

        documents = archive["documents"] = Section(
            title=_(u"Documents"),
            description=_(u"Visit the digital document repository"),
            default_name="browse-archive")
            
        
        def to_locatable_container(domain_class, *domain_containers):
            provideAdapter(location.ContainerLocation(*domain_containers),
                       (implementedBy(domain_class), ILocation))
        
        # archive/records
        documents[u"bills"] = domain.BillContainer()
        to_locatable_container(domain.Bill, documents[u"bills"])

        documents[u"motions"] = domain.MotionContainer()
        to_locatable_container(domain.Motion, documents[u"motions"])
        
        documents[u"questions"] = domain.QuestionContainer()
        to_locatable_container(domain.Question, documents[u"questions"])
        
        documents[u"agendaitems"] = domain.AgendaItemContainer()
        to_locatable_container(domain.AgendaItem, documents[u"agendaitems"])

        documents[u"tableddocuments"] = domain.TabledDocumentContainer()
        to_locatable_container(domain.TabledDocument, documents[u"tableddocuments"])
        
        documents[u"reports"] = domain.ReportContainer()
        to_locatable_container(domain.Report, documents[u"reports"])
        #provideAdapter(location.ContainerLocation(tableddocuments, documents[u"reports"]),
        #               (implementedBy(domain.Report), ILocation))
        
        records[u"parliaments"] = domain.ParliamentContainer()
        to_locatable_container(domain.Parliament, records[u"parliaments"])
        
        records[u"politicalgroups"] = domain.PoliticalGroupContainer()
        to_locatable_container(domain.PoliticalGroup, records[u"politicalgroups"])
        
        records[u"constituencies"] = domain.ConstituencyContainer()
        to_locatable_container(domain.Constituency, records[u"constituencies"])
        
        records[u"committees"] = domain.CommitteeContainer()
        to_locatable_container(domain.Committee, records[u"committees"])

        #records[u"mps"] = domain.MemberOfParliamentContainer()
        #provideAdapter(location.ContainerLocation(records[u"mps"]),
        #               (implementedBy(domain.MemberOfParliament), ILocation))
        
        ##########
        # Admin User Interface
        # Administration section
        
        content = admin["content"] = Section(
            title=_(u"Content"),
            description=_(u"browse the content"),
            marker=model_interfaces.IBungeniAdmin,
            default_name="browse-admin")

        admin["settings"] = Section(
            title=_(u"Settings"),
            description=_(u"settings"),
            marker=model_interfaces.IBungeniAdmin,
            default_name="settings")
        
        content[u"parliaments"] = domain.ParliamentContainer()
        to_locatable_container(domain.Parliament, content[u"parliaments"])
        
        content[u'users'] = domain.UserContainer()
        to_locatable_container(domain.User, content[u"users"])
        
        content[u'headings'] = domain.HeadingContainer()
        to_locatable_container(domain.Heading, content[u"headings"])
        
        content[u"constituencies"] = domain.ConstituencyContainer()
        to_locatable_container(domain.Constituency, content[u"constituencies"])
        
        content[u"provinces"] = domain.ProvinceContainer()
        to_locatable_container(domain.Province, content[u"provinces"])
        
        content[u"regions"] = domain.RegionContainer()
        to_locatable_container(domain.Region, content[u"regions"])
        
        content[u"parties"] = domain.PoliticalPartyContainer()
        to_locatable_container(domain.PoliticalParty, content[u"parties"])
        
