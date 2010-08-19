import re
import os
from appy.pod.renderer import Renderer
from zope.publisher.browser import BrowserView
import time
import datetime
timedelta = datetime.timedelta
import tempfile
from zope.security.proxy import removeSecurityProxy
import htmlentitydefs
from xml.dom.minidom import parseString
from bungeni.ui import zcml
from interfaces import IOpenOfficeConfig
from zope.component import getUtility
from ore.alchemist import Session
from bungeni.models import domain
from zope import interface
from zope.formlib import form
from zope.formlib import namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from zope import schema
from bungeni.ui.widgets import SelectDateWidget
from bungeni.ui.calendar import utils
from bungeni.ui.tagged import get_states
from bungeni.ui.i18n import _
from bungeni.ui.utils import misc, url as ui_url, queries, debug
from bungeni.ui.menu import get_actions
from bungeni.ui.forms.common import set_widget_errors
from bungeni.ui import vocabulary
from bungeni.core.location import location_wrapped
from bungeni.core.interfaces import ISchedulingContext
import zope.securitypolicy.interfaces
from bungeni.core.odf import OpenDocument
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.form.browser import MultiCheckBoxWidget as _MultiCheckBoxWidget
from sqlalchemy.orm import eagerload
import sqlalchemy.sql.expression as sql
import operator
from bungeni.models import domain
from bungeni.models.utils import get_db_user_id
from bungeni.models.utils import get_current_parliament
from bungeni.models.interfaces import IGroupSitting
from bungeni.server.interfaces import ISettings
from bungeni.ui.forms.common import AddForm
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
class TIME_SPAN:
    daily = _(u"Daily")
    weekly = _(u"Weekly")

def verticalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"verticalMultiCheckBoxWidget"
    widget.orientation = 'vertical'
    return widget

def horizontalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"horizontalMultiCheckBoxWidget"
    widget.orientation = 'horizontal'
    return widget

def availableItems(context):
    items = ('Bills',
                'Agenda Items',
                'Motions',
                'Questions',
                'Tabled Documents',
                )
    return SimpleVocabulary.fromValues(items)

def billOptions(context):
    items = ('Title',
             'Summary',
             'Text',
             'Owner',
             'Cosignatories',
            )
    return SimpleVocabulary.fromValues(items)

def agendaOptions(context):
    items = ('Title',
             'Text',
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def motionOptions(context):
    items = ('Title',
             'Number',
             'Text',
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def tabledDocumentOptions(context):
    items = ('Title',
             'Number',
             'Text',
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def questionOptions(context):
    items = ('Title',
             'Number',
             'Text',
             'Owner',
             #'Response',
             'Type',
            )
    return SimpleVocabulary.fromValues(items)


class ReportView(form.PageForm):

    main_result_template = ViewPageTemplateFile('templates/main_reports.pt')
    result_template = ViewPageTemplateFile('templates/reports.pt')

    def __init__(self, context, request):
        super(ReportView, self).__init__(context, request)

    class IReportForm(interface.Interface):
        doc_type = schema.Choice(
                    title=_(u"Document Type"),
                    description=_(u"Type of document to be produced"),
                    values=['Order of the day',
                             'Weekly Business',
                             'Questions of the week'],
                    required=True
                    )
        date = schema.Date(
            title=_(u"Date"),
            description=_(u"Choose a starting date for this report"),
            required=True)
        item_types = schema.List(title=u'Items to include',
                   required=False,
                   value_type=schema.Choice(
                    vocabulary="Available Items"),
                   )
        bills_options = schema.List(title=u'Bill options',
                       required=False,
                       value_type=schema.Choice(
                       vocabulary='Bill Options'),
                         )
        agenda_items_options = schema.List(title=u'Agenda options',
                                        required=False,
                                        value_type=schema.Choice(
                                        vocabulary='Agenda Options'),)
        motions_options = schema.List(title=u'Motion options',
                                        required=False,
                                        value_type=schema.Choice(
                                        vocabulary='Motion Options'),)
        questions_options = schema.List(title=u'Question options',
                                          required=False,
                                          value_type=schema.Choice(
                                          vocabulary='Question Options'),)
        tabled_documents_options = schema.List(title=u'Tabled Document options',
                                          required=False,
                                          value_type=schema.Choice(
                                          vocabulary='Tabled Document Options'),)
        note = schema.TextLine(title=u'Note',
                                required=False,
                                description=u'Optional note regarding this report'
                        )

    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(IReportForm)
    form_fields['item_types'].custom_widget = horizontalMultiCheckBoxWidget
    form_fields['bills_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['agenda_items_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['motions_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['questions_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['tabled_documents_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['date'].custom_widget = SelectDateWidget


    def setUpWidgets(self, ignore_request=False):
        class context:
            item_types = 'Bills'
            bills_options = 'Title'
            agenda_items_options = 'Title'
            questions_options = 'Title'
            motions_options = 'Title'
            tabled_documents_options = 'Title'
            note = None
            date = None
            doc_type = 'Order of the day'
        self.adapters = {
            self.IReportForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)
    def update(self):
        super(ReportView, self).update()
        set_widget_errors(self.widgets, self.errors)

    def validate(self, action, data):
        errors = super(ReportView, self).validate(action, data)
        self.time_span = TIME_SPAN.daily
        if 'doc_type' in data:
            if data['doc_type'] == "Order of the day":
                self.time_span = TIME_SPAN.daily
            elif data['doc_type'] == "Proceedings of the day":
                self.time_span = TIME_SPAN.daily
            elif data['doc_type'] == "Weekly Business":
                self.time_span = TIME_SPAN.weekly
            elif data['doc_type'] == "Questions of the week":
                self.time_span = TIME_SPAN.weekly

        if IGroupSitting.providedBy(self.context):
            self.start_date = datetime.date(
                self.context.start_date.year,
                self.context.start_date.month,
                self.context.start_date.day)
        elif ISchedulingContext.providedBy(self.context):
            if 'date' in data:
                self.start_date = data['date']
        else:
            self.start_date = datetime.today().date()

        self.end_date = self.get_end_date(self.start_date, self.time_span)

        parliament = queries.get_parliament_by_date_range(self, self.start_date, self.end_date)
        #session = queries.get_session_by_date_range(self, start_date, end_date)

        if parliament is None:
            errors.append(interface.Invalid(
                _(u"A parliament must be active in the period"),
                "date"))

        return errors

    @form.action(_(u"Preview"))
    def handle_preview(self, action, data):
        self.process_form(data)
        self.save_link = ui_url.absoluteURL(self.context, self.request) + "/save-report"
        self.body_text = self.result_template()
        return self.main_result_template()

    def get_end_date(self, start_date, time_span):
        if time_span is TIME_SPAN.daily:
            return start_date + timedelta(days=1)
        elif time_span is TIME_SPAN.weekly:
            return start_date + timedelta(weeks=1)

        raise RuntimeError("Unknown time span: %s" % time_span)

    def get_sittings(self, start, end):
            """ return the sittings with scheduled items for 
                the given daterange"""
            session = Session()
            query = session.query(domain.GroupSitting).filter(
                sql.and_(
                    domain.GroupSitting.start_date.between(start, end),
                    domain.GroupSitting.group_id == self.context.group_id)
                    ).order_by(domain.GroupSitting.start_date
                    ).options(
                        eagerload('sitting_type'),
                        eagerload('item_schedule'),
                        eagerload('item_schedule.item'),
                        eagerload('item_schedule.discussion'))
            items = query.all()
            for item in items:
                if self.display_minutes:
                    item.item_schedule.sort(key=operator.attrgetter('real_order'))
                else:
                    item.item_schedule.sort(key=operator.attrgetter('planned_order'))
                    item.sitting_type.sitting_type = item.sitting_type.sitting_type.capitalize()
            return items

    def process_form(self, data):
        class optionsobj(object):
            '''Object that holds all the options.'''
            pass
        self.options = optionsobj()
        if not hasattr(self, 'doc_type'):
            if 'doc_type' in data:
                self.doc_type = data['doc_type']
        self.sittings = []

        if IGroupSitting.providedBy(self.context):
            session = Session()
            st = self.context.sitting_id
            sitting = session.query(domain.GroupSitting).get(st)
            self.sittings.append(sitting)
            back_link = ui_url.absoluteURL(self.context, self.request) + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            self.sittings = self.get_sittings(self.start_date, self.end_date)
            back_link = ui_url.absoluteURL(self.context, self.request)
        else:
            raise NotImplementedError
        count = 0
        self.ids = ""
        for s in self.sittings:
            self.ids = self.ids + str(s.sitting_id) + ","
        def cleanup(string):
            return string.lower().replace(" ", "_")

        for item_type in data['item_types']:
            itemtype = cleanup(item_type)
            setattr(self.options, itemtype, True)
            for option in data[itemtype + "_options"]:
                setattr(self.options, cleanup(itemtype + "_" + option), True)

        if self.display_minutes:
            self.link = ui_url.absoluteURL(self.context, self.request) + '/votes-and-proceedings'
        else :
            self.link = ui_url.absoluteURL(self.context, self.request) + '/agenda'

        try:
            self.group = self.context.get_group()
        except:
            session = Session()
            self.group = session.query(domain.Group).get(self.context.group_id)

class GroupSittingContextAgendaReportView(ReportView):
    display_minutes = False
    doc_type = "Sitting Agenda"
    note = ""
    form_fields = ReportView.form_fields.omit('doc_type', 'date')

class GroupSittingContextMinutesReportView(ReportView):
    display_minutes = True
    doc_type = "Votes and Proceedings"
    note = ""
    form_fields = ReportView.form_fields.omit('doc_type', 'date')

class SchedulingContextAgendaReportView(ReportView):
    display_minutes = False
    note = ""

class SchedulingContextMinutesReportView(ReportView):
    display_minutes = True
    note = ""

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class DownloadDocument(BrowserView):

    #path to the odt template
    odt_file = os.path.dirname(__file__) + '/calendar/agenda.odt'
    def __init__(self, context, request):
        self.report = removeSecurityProxy(context)
        super(DownloadDocument, self).__init__(context, request)

    def cleanupText(self):
        '''This function generates an ODT document from the text of a report'''
        #This should really be at the top of this file.
        #Leaving it here for the time being so that having 
        #libtidy is not a requirement to run bungeni
        import tidy
        body_text = self.report.body_text
        #utidylib options
        options = dict(output_xhtml=1,
                    add_xml_decl=1,
                    indent=1,
                    tidy_mark=0,
                    char_encoding='utf8',
                    quote_nbsp=0)
        #remove html entities from the text
        ubody_text = unescape(body_text)
        #clean up xhtml using tidy
        aftertidy = tidy.parseString(ubody_text.encode('utf8'), **options)
        #tidy returns a <tidy.lib._Document object>
        dom = parseString(str(aftertidy))
        nodeList = dom.getElementsByTagName("body")
        text = ""
        for childNode in nodeList[0].childNodes:
            text += childNode.toxml()
        dom.unlink()
        return text

class DownloadODT(DownloadDocument):
    #appy.Renderer expects a file name of a file that does not exist.
    tempFileName = os.path.dirname(__file__) + '/tmp/%f.odt' % (time.time())
    def __call__(self):
        self.request.response.setHeader('Content-type',
                                        'application/vnd.oasis.opendocument.text')
        self.request.response.setHeader('Content-disposition',
                                        'inline;filename="' +
                                        removeSecurityProxy(self.report.report_type) + "_" +
                                        removeSecurityProxy(self.report.start_date).strftime('%Y-%m-%d') + '.odt"')
        session = Session()
        report = session.query(domain.Report).get(self.report.report_id)
        d = dict([(f.file_title, f.file_data) for f in report.attached_files])
        if "odt" not in d.keys():
            params = {}
            params['body_text'] = self.cleanupText()
            renderer = Renderer(self.odt_file, params, self.tempFileName)
            renderer.run()
            f = open(self.tempFileName, 'rb')
            doc = f.read()
            f.close()
            os.remove(self.tempFileName)
            attached_file = domain.AttachedFile()
            attached_file.file_title = "odt"
            attached_file.file_data = doc
            attached_file.language = report.language
            report.attached_files.append(attached_file)
            notify(ObjectCreatedEvent(attached_file))
            session.add(report)
            session.commit()
            return doc
        else:
            return d["odt"].__str__()


class  DownloadPDF(DownloadDocument):
    #appy.Renderer expects a file name of a file that does not exist.
    tempFileName = os.path.dirname(__file__) + '/tmp/%f.pdf' % (time.time())

    def __call__(self):
        self.request.response.setHeader('Content-type', 'application/pdf')
        self.request.response.setHeader('Content-disposition', 'inline;filename="'
                            + removeSecurityProxy(self.report.report_type) + "_"
                            + removeSecurityProxy(self.report.start_date).strftime('%Y-%m-%d') + '.pdf"')
        
        
        session = Session()
        report = session.query(domain.Report).get(self.report.report_id)
        d = dict([(f.file_title, f.file_data) for f in report.attached_files])
        if "pdf" not in d.keys():
            params = {}
            params['body_text'] = self.cleanupText()
            openofficepath = getUtility(IOpenOfficeConfig).getPath()
            renderer = Renderer(self.odt_file, params, self.tempFileName, pythonWithUnoPath=openofficepath)
            renderer.run()
            f = open(self.tempFileName, 'rb')
            doc = f.read()
            f.close()
            os.remove(self.tempFileName)
            attached_file = domain.AttachedFile()
            attached_file.file_title = "pdf"
            attached_file.file_data = doc
            attached_file.language = report.language
            report.attached_files.append(attached_file)
            notify(ObjectCreatedEvent(attached_file))
            session.add(report)
            session.commit()
            return doc
        else:
            return d["pdf"].__str__()

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
        note = schema.TextLine(title=u'Note',
                                required=False,
                                description=u'Optional note regarding this report'
                        )
        report_type = schema.TextLine(title=u'Report Type',
                                required=True,
                                description=u'Report Type'
                        )
        body_text = schema.Text(title=u'Report Text',
                                required=True,
                                description=u'Report Type'
                        )
        sittings = schema.TextLine(
                    title=_(u"Sittings included in this report"),
                    description=_(u"Sittings included in this report"),
                    required=True
                               )
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(ISaveReportForm)

    def setUpWidgets(self, ignore_request=False):
        class context:
            start_date = None
            end_date = None
            body_text = None
            note = None
            report_type = None
            sittings = None
        self.adapters = {
            self.ISaveReportForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
                    adapters=self.adapters, ignore_request=ignore_request)

    @form.action(_(u"Save"))
    def handle_save(self, action, data):
        report = domain.Report()
        session = Session()
        report.body_text = data['body_text']
        report.start_date = data['start_date']
        report.end_date = data['end_date']
        report.note = data['note']
        report.report_type = data['report_type']
        report.short_name = data['report_type']
        owner_id = get_db_user_id()
        '''!+TODO(Miano, 18/08/2010) The admin user is currently not a db user
            thus the line above returns None when the admin publishes a report.
            to go around this if it returns None, just query the db for users
            and set the owner id to be the first result'''
        if owner_id is not None:
            report.owner_id = owner_id
        else:
            query = session.query(domain.User)
            results = query.all()
            report.owner_id = results[0].user_id
        report.language = "en"
        report.created_date = datetime.datetime.now()
        report.group_id = self.context.group_id
        session.add(report)
        notify(ObjectCreatedEvent(report))
        ids = data["sittings"].split(",")
        for id in ids:
            try:
                sit_id = int(id)
            except:
                continue
            sitting = session.query(domain.GroupSitting).get(sit_id)
            sr = domain.SittingReport()
            sr.report = report
            sr.sitting = sitting
            session.add(sr)
        session.commit()

        if IGroupSitting.providedBy(self.context):
            back_link = './schedule'
        elif ISchedulingContext.providedBy(self.context):
            back_link = './'
        else:
            raise NotImplementedError
        self.request.response.redirect(back_link)



