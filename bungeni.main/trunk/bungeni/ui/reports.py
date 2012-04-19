# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt
"""Sittings and Calendar report browser views

$Id$
"""

log = __import__("logging").getLogger("bungeni.ui.reports")

import operator
import datetime
timedelta = datetime.timedelta

from zope import interface, component
from zope import schema
from zope.formlib import form
from zope.formlib import namedtemplate
from zope.formlib.widgets import MultiCheckBoxWidget as _MultiCheckBoxWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.schema.vocabulary import SimpleVocabulary
from zope.security.proxy import removeSecurityProxy
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.component.hooks import getSite

from bungeni.alchemist import Session
from bungeni.models import domain
from bungeni.models.utils import get_db_user_id
from bungeni.models.interfaces import ISitting

from bungeni.core.interfaces import ISchedulingContext
from bungeni.core.workflow.interfaces import IWorkflow, IWorkflowTransitionEvent
from bungeni.core.language import get_default_language

from bungeni.ui import widgets
from bungeni.ui.i18n import _
from bungeni.ui.utils import url, queries, date
from bungeni.ui import forms
from bungeni.ui.interfaces import IWorkspaceReportGeneration
from bungeni.ui.reporting import generators
from bungeni.ui.calendar.data import ExpandedSitting

from bungeni.utils import register

class TIME_SPAN:
    daily = _(u"Daily")
    weekly = _(u"Weekly")

def verticalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"verticalMultiCheckBoxWidget"
    widget.orientation = "vertical"
    return widget

def horizontalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"horizontalMultiCheckBoxWidget"
    widget.orientation = "horizontal"
    return widget

def availableItems(context):
    items = (
        _(u"Bills"),
        _(u"Agenda Items"),
        _(u"Motions"),
        _(u"Questions"),
        _(u"Tabled Documents"),
    )
    return SimpleVocabulary.fromValues(items)

def billOptions(context):
    items = (
        _(u"Title"),
        _(u"Summary"),
        _(u"Text"),
        _(u"Owner"),
        _(u"Signatories"),
    )
    return SimpleVocabulary.fromValues(items)

def agendaOptions(context):
    items = (
        _(u"Title"),
        _(u"Text"),
        _(u"Owner"),
    )
    return SimpleVocabulary.fromValues(items)

def motionOptions(context):
    items = (
        _(u"Title"),
        _(u"Number"),
        _(u"Text"),
        _(u"Owner"),
        _(u"Signatories"),
    )
    return SimpleVocabulary.fromValues(items)

def tabledDocumentOptions(context):
    items = (
        _(u"Title"),
        _(u"Number"),
        _(u"Text"),
        _(u"Owner"),
        _(u"Signatories"),
    )
    return SimpleVocabulary.fromValues(items)

def questionOptions(context):
    items = (
        _(u"Title"),
        _(u"Number"),
        _(u"Text"),
        _(u"Owner"),
        #"Response",
        _(u"Type"),
        _(u"Signatories"),
    )
    return SimpleVocabulary.fromValues(items)


class DateTimeFormatMixin(object):
    """Helper methods to format and localize date and time objects
    """
    def format_date(self, date_time, category="dateTime"):
        formatter = date.getLocaleFormatter(self.request, category=category)
        return formatter.format(date_time)

    def l10n_dates(self, date_time, dt_format="dateTime"):
        if date_time:
            try:
                formatter = self.request.locale.dates.getFormatter(dt_format)
                return formatter.format(date_time)
            except AttributeError:
                return date_time
        return date_time

class IReportBuilder(interface.Interface):
    report_type = schema.Choice(title=_(u"Report Type"),
        description=_(u"Choose template to use in generating Report"),
        vocabulary="bungeni.vocabulary.ReportXHTMLTemplates"
    )
    start_date = schema.Date(title=_(u"Start Date"),
        description=_(u"Start date for this Report")
    )
    publication_number = schema.TextLine(title=_(u"Publication Number"),
        description=_(u"Optional publication number for this Report"),
        required=False
    )

class ReportBuilder(form.Form, DateTimeFormatMixin):
    template = namedtemplate.NamedTemplate("alchemist.form")
    form_fields = form.fields(IReportBuilder)
    form_fields["start_date"].custom_widget = widgets.SelectDateWidget
    sittings = []
    publication_date = datetime.datetime.today().date()
    publication_number = ""
    title = _(u"Report Title")
    generated_content = None
    show_preview = False
    language = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        interface.declarations.alsoProvides(removeSecurityProxy(self.context), 
            IWorkspaceReportGeneration
        )
        super(ReportBuilder, self).__init__(context, request)

    def get_end_date(self, start_date, hours):
        end_date = start_date + datetime.timedelta(seconds=hours*3600)
        return end_date

    def buildSittings(self, start_date, end_date):
        if ISitting.providedBy(self.context):
            trusted = removeSecurityProxy(self.context)
            order="real_order"
            trusted.item_schedule.sort(key=operator.attrgetter(order))
            self.sittings.append(trusted)
        else:
            sittings = ISchedulingContext(self.context).get_sittings(
                start_date, end_date
            ).values()
            self.sittings = map(removeSecurityProxy, sittings)
        self.sittings = [ ExpandedSitting(sitting) for sitting in self.sittings ]

    def generateContent(self, data):
        self.start_date = (data.get("start_date") or 
            datetime.datetime.today().date()
        )
        generator = generators.ReportGeneratorXHTML(data.get("report_type"))
        self.language = generator.language
        self.title = generator.title
        self.language = generator.language
        self.publication_number = data.get("publication_number")
        self.end_date = self.get_end_date(self.start_date, generator.coverage)
        self.buildSittings(self.start_date, self.end_date)
        generator.context = self
        return generator.generateReport()

    @form.action(_(u"Preview"), name="preview")
    def handle_preview(self, action, data):
        """Generate preview of the report
        """
        self.show_preview = True
        self.generated_content = self.generateContent(data)
        self.status = _(u"See the preview of the report below")
        return self.template()

    @form.action(_(u"Publish"), name="publish")
    def handle_publish(self, action, data):
        self.generated_content = self.generateContent(data)
        
        if not hasattr(self.context, "group_id"):
            context_group_id = ISchedulingContext(self.context).group_id
        else:
            context_group_id = self.context.group_id
        
        report = domain.Report(
            short_title=self.title,
            start_date=self.start_date,
            end_date=self.end_date,
            body=self.generated_content,
            owner_id=get_db_user_id(), # !+GROUP_AS_OWNER
            language=self.language,
            group_id=context_group_id
        )
        session = Session()
        session.add(report)
        session.flush()
        notify(ObjectCreatedEvent(report))
        self.status = _(u"Report has been processed and saved")
        
        return self.template()

class ReportView(form.PageForm, DateTimeFormatMixin):
    main_result_template = ViewPageTemplateFile("templates/main-reports.pt")
    result_template = ViewPageTemplateFile(
        "templates/default-report-sitting.pt"
    )
    display_minutes = None
    include_text = True

    def __init__(self, context, request):
        self.site_url = url.absoluteURL(getSite(), request)
        super(ReportView, self).__init__(context, request)

    def check_option(self, doctype, option=""):
        opt_key = "%s_%s" %(doctype, option) if option else doctype
        return hasattr(self.options, opt_key)

    class IReportForm(interface.Interface):
        short_name = schema.Choice(
            title=_(u"Document Type"),
            description=_(u"Type of report to be produced"),
            values=["Order of the day", "Weekly Business", 
                "Questions of the week"],
            required=True)
        date = schema.Date(
            title=_(u"Date"),
            description=_(u"Choose a starting date for this report"),
            required=True)
        item_types = schema.List(title=u"Items to include",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.AvailableItems"))
        bills_options = schema.List(title=u"Bill options",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.BillOptions"))
        agenda_items_options = schema.List(title=u"Agenda options",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.AgendaOptions"))
        motions_options = schema.List(title=u"Motion options",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.MotionOptions"))
        questions_options = schema.List(title=u"Question options",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.QuestionOptions"))
        tabled_documents_options = schema.List(title=u"Tabled Document options",
            required=False,
            value_type=schema.Choice(
                vocabulary="bungeni.vocabulary.TabledDocumentOptions"))
        note = schema.TextLine(title=u"Note",
            required=False,
            description=u"Optional note regarding this report")
    
    template = namedtemplate.NamedTemplate("alchemist.form")
    form_fields = form.Fields(IReportForm)
    form_fields["item_types"].custom_widget = horizontalMultiCheckBoxWidget
    form_fields["bills_options"].custom_widget = verticalMultiCheckBoxWidget
    form_fields["agenda_items_options"].custom_widget = verticalMultiCheckBoxWidget
    form_fields["motions_options"].custom_widget = verticalMultiCheckBoxWidget
    form_fields["questions_options"].custom_widget = verticalMultiCheckBoxWidget
    form_fields["tabled_documents_options"].custom_widget = verticalMultiCheckBoxWidget
    form_fields["date"].custom_widget = widgets.SelectDateWidget
    def setUpWidgets(self, ignore_request=False):
        class context:
            item_types = "Bills"
            bills_options = "Title"
            agenda_items_options = "Title"
            questions_options = "Title"
            motions_options = "Title"
            tabled_documents_options = "Title"
            note = None
            date = None
            short_name = _(u"Order of the day")
        self.adapters = {self.IReportForm: context}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, 
            self.prefix, 
            self.context, 
            self.request,
            adapters=self.adapters, 
            ignore_request=ignore_request)
    def update(self):
        super(ReportView, self).update()
        forms.common.set_widget_errors(self.widgets, self.errors)
        
    def get_end_date(self, start_date, time_span):
        if time_span is TIME_SPAN.daily:
            return start_date + timedelta(days=1)
        elif time_span is TIME_SPAN.weekly:
            return start_date + timedelta(weeks=1)
        raise RuntimeError("Unknown time span: %s" % time_span)
    
    def time_span(self,data):
        if "short_name" in data:
            if data["short_name"] == u"Order of the day":
                return TIME_SPAN.daily
            elif data["short_name"] == u"Proceedings of the day":
                return TIME_SPAN.daily
            elif data["short_name"] == u"Weekly Business":
                return TIME_SPAN.weekly
            elif data["short_name"] == u"Questions of the week":
                return TIME_SPAN.weekly
        else:
            return TIME_SPAN.daily
    
    def validate(self, action, data):
        errors = super(ReportView, self).validate(action, data)
        time_span = self.time_span(data)
        if ISitting.providedBy(self.context):
            if not self.context.items:
                errors.append(interface.Invalid(
                _(u"The sitting has no scheduled items")))
        else:
            start_date = data["date"] if "date" in data else \
                                                datetime.datetime.today().date()
            end_date = self.get_end_date(start_date, time_span)
            try:
                ctx = ISchedulingContext(self.context)
            except:
                m = u"You are trying to generate a report outside scheduling"
                errors.append(interface.Invalid(_(m)))
            sittings = ctx.get_sittings(start_date, end_date).values()
            if not sittings:
                m = u"The period selected has no sittings"
                errors.append(interface.Invalid(_(m), "date"))
            
            parliament = queries.get_parliament_by_date_range(
                start_date, end_date
            )
            if parliament is None:
                m = u"A parliament must be active in the period"
                errors.append(interface.Invalid(_(m), "date"))
        return errors
    
    @form.action(_(u"Preview"), name="preview")
    def handle_preview(self, action, data):
        self.process_form(data)
        self.save_link = "%s/save-report" % (
            url.absoluteURL(self.context, self.request))
        self.body = self.result_template()
        return self.main_result_template()

    def process_form(self, data):
        class optionsobj(object):
            """Object that holds all the options."""
        self.options = optionsobj()
        if not hasattr(self, "short_name"):
            if "short_name" in data:
                self.short_name = data["short_name"]
        self.sittings = []
        if ISitting.providedBy(self.context):
            trusted = removeSecurityProxy(self.context)
            order = "real_order" if self.display_minutes else "planned_order"
            trusted.item_schedule.sort(key=operator.attrgetter(order))
            self.sittings.append(trusted)
            self.start_date = self.context.start_date
            self.end_date = self.get_end_date(
                self.start_date, self.time_span(data))
        else:
            self.start_date = data["date"] if "date" in data \
                else datetime.datetime.today().date()
            self.end_date = self.get_end_date(
                self.start_date, self.time_span(data))
            sittings = ISchedulingContext(self.context).get_sittings(
                self.start_date, self.end_date).values()
            self.sittings = map(removeSecurityProxy,sittings)
        self.ids = ""
        for sitting in self.sittings:
            self.ids += str(sitting.sitting_id) + ","
        def cleanup(string):
            return string.lower().replace(" ", "_")
        for item_type in data["item_types"]:
            itemtype = cleanup(item_type)
            type_key = itemtype.rstrip("s").replace("_", "")
            setattr(self.options, type_key, True)
            setattr(self.options, itemtype, True)
            for option in data[itemtype + "_options"]:
                opt_key = "".join((cleanup(itemtype.rstrip("s")).replace("_",""),
                    "_", cleanup(option)
                ))
                setattr(self.options, opt_key, True)
        if self.display_minutes:
            self.link = "%s/votes-and-proceedings" % (
                url.absoluteURL(self.context, self.request))
        else :
            self.link = "%s/agenda" % (
                url.absoluteURL(self.context, self.request))
        try:
            self.group = self.context.group
        except:
            self.group = ISchedulingContext(self.context).get_group()

class SittingContextAgendaReportView(ReportView):
    display_minutes = False
    include_text = False
    short_name = _(u"Sitting Agenda")
    note = ""
    form_fields = ReportView.form_fields.omit("short_name", "date")

class SittingContextMinutesReportView(ReportView):
    display_minutes = True
    short_name = "Sitting Votes and Proceedings"
    note = ""
    form_fields = ReportView.form_fields.omit("short_name", "date")

class SchedulingContextAgendaReportView(ReportView):
    result_template = ViewPageTemplateFile(
        "templates/default-report-scheduling.pt"
    )
    display_minutes = False
    include_text = False
    note = ""

class SchedulingContextMinutesReportView(ReportView):
    display_minutes = True
    note = ""

class SaveReportView(form.PageForm):

    def __init__(self, context, request):
        super(SaveReportView, self).__init__(context, request)

    class ISaveReportForm(interface.Interface):
        start_date = schema.Date(
            title=_(u"Date"),
            description=_(u"Choose a starting date for this report"),
            required=True)
        end_date = schema.Date(
            title=_(u"Date"),
            description=_(u"Choose an end date for this report"),
            required=True)
        note = schema.TextLine(title=u"Note",
            description=u"Optional note regarding this report",
            required=False)
        short_name = schema.TextLine(title=u"Report Type",
            description=u"Report Type",
            required=True)
        body = schema.Text(title=u"Report Text",
            description=u"Report Type",
            required=True)
        sittings = schema.TextLine(title=_(u"Sittings included in this report"),
            description=_(u"Sittings included in this report"),
            required=False)
    template = namedtemplate.NamedTemplate("alchemist.form")
    form_fields = form.Fields(ISaveReportForm)
    
    def setUpWidgets(self, ignore_request=False):
        class context:
            start_date = None
            end_date = None
            body = None
            note = None
            short_name = None
            sittings = None
        self.adapters = {self.ISaveReportForm: context}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, 
            self.prefix, 
            self.context, 
            self.request,
            adapters=self.adapters, 
            ignore_request=ignore_request
        )
    
    @form.action(_(u"Save"), name="save")
    def handle_save(self, action, data):
        report = domain.Report()
        session = Session()
        report.body = data["body"]
        report.start_date = data["start_date"]
        report.end_date = data["end_date"]
        report.note = data["note"]
        report.short_name = data["short_name"]
        report.owner_id = get_db_user_id() # !+GROUP_AS_OWNER
        report.language = get_default_language()
        report.created_date = datetime.datetime.now()
        if not hasattr(self.context, "group_id"):
            report.group_id = ISchedulingContext(self.context).group_id
        else:
            report.group_id = self.context.group_id
        session.add(report)
        session.flush()
        notify(ObjectCreatedEvent(report))
        if "sittings" in data.keys():
            try:
                ids = data["sittings"].split(",")
                for id_number in ids:
                    sit_id = int(id_number)
                    sitting = session.query(domain.Sitting).get(sit_id)
                    sr = domain.SittingReport()
                    sr.report = report
                    sr.sitting = sitting
                    session.add(sr)
                    notify(ObjectCreatedEvent(report))
            except:
                #if no sittings are present in report or some other error occurs
                pass
        session.flush()
        
        if ISitting.providedBy(self.context):
            back_link = "./schedule"
        else:
            back_link = "./"
        self.request.response.redirect(back_link)

class SittingReportContext(object):
    def __init__(self, sittings):
        self.sittings = sittings

# Event handler that publishes reports on sitting status change
# if the status is published_agenda or published_minutes
# it generates report based on the default template and publishes it
@register.handler(adapts=(ISitting, IWorkflowTransitionEvent))
def default_reports(sitting, event):
    if sitting.status in IWorkflow(sitting).get_state_ids(tagged=["published"]):
        sitting = removeSecurityProxy(sitting)
        sittings = [ExpandedSitting(sitting)]
        report_context = SittingReportContext(sittings)
        report = domain.Report()
        session = Session()
        report.start_date = sitting.start_date
        report.end_date = sitting.end_date
        # !+GROUP_AS_OWNER(mr, apr-2012) we assume for now that the "owner" of
        # the report is the currently logged in user.
        report.owner_id = get_db_user_id()
        report.created_date = datetime.datetime.now()
        report.group_id = sitting.group_id
        
        # generate using html template in bungeni_custom
        vocabulary = component.queryUtility(
            schema.interfaces.IVocabularyFactory, 
            "bungeni.vocabulary.ReportXHTMLTemplates"
        )
        preview_template = filter(
            lambda t: t.title=="Weekly Business", vocabulary.terms
        )[0]
        doc_template = preview_template.value
        generator = generators.ReportGeneratorXHTML(doc_template)
        generator.context = report_context
        report.language = generator.language
        
        if sitting.status == "published_agenda":
            report.short_name = generator.title = _(u"Sitting Agenda")
        elif sitting.status == "published_minutes":
            report.short_name = generator.title = \
                _(u"Sitting Votes and Proceedings")
        report.body = generator.generateReport()
        session.add(report)
        session.flush()
        notify(ObjectCreatedEvent(report))
        sr = domain.SittingReport()
        sr.report = report
        sr.sitting = sitting
        session.add(sr)
        session.flush()
        notify(ObjectCreatedEvent(sr))


