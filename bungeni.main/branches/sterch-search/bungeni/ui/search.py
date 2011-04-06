"""
User interface for Content Search


Todo - Canonical URL on index of results, tuple,
       AbsoluteURL adapter for results
       mark result class with interface


Supported xapian query operators
 |  OP_AND = 0
 |
 |  OP_AND_MAYBE = 4
 |
 |  OP_AND_NOT = 2
 |
 |  OP_ELITE_SET = 10
 |
 |  OP_FILTER = 5
 |
 |  OP_NEAR = 6
 |
 |  OP_OR = 1
 |
 |  OP_PHRASE = 7
 |
 |  OP_SCALE_WEIGHT = 9
 |
 |  OP_SYNONYM = 13
 |
 |  OP_VALUE_GE = 11
 |
 |  OP_VALUE_LE = 12
 |
 |  OP_VALUE_RANGE = 8
 |
 |  OP_XOR = 3
 |
"""

import time, simplejson, urllib
from bungeni.ui import forms
from ore.xapian import interfaces

from zope import interface, schema, component
from zope.publisher.browser import BrowserView, BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zope.formlib import form
from zope.cachedescriptors.property import CachedProperty
from zc.table import table, column
from bungeni.core.i18n import _
from bungeni.core.translation import language_vocabulary_factory as languages
from bungeni.ui.widgets import SelectDateWidget
from bungeni.core import index
from zope.dottedname import resolve
from bungeni.alchemist import Session
from bungeni.ui.workflow import workflow_vocabulary_factory
from bungeni.models.domain import Motion
from bungeni.alchemist import ui

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope import formlib
from ore.xapian.interfaces import IIndexer


def get_statuses_vocabulary(klass):
    try:
        obj = klass()
        return workflow_vocabulary_factory(obj)
    except Exception:
        return None


class ISearch(interface.Interface):

    full_text = schema.TextLine(title=_("Query"), required=False)


class IAdvancedSearch(ISearch):

    language = schema.Choice(title=_("Language"), values=("en", "fr", "pt", "sw", "it", "en-ke"), required=False)

    content_type = schema.Choice(title=_("Content type"), values=("Question", "Motion"), required=False)

    #status = schema.Choice(title=_("Status"), vocabulary=SimpleVocabulary([]), required=False)

    status_date = schema.Date(title=_("Status date"), required=False)


class ISearchResult(interface.Interface):

    title = schema.TextLine(title=_("Title"), required=False)
    annotation = schema.Text(title=_("Annotation"), required=False)


class UserToSearchResult(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return "%s - %s" % (self.context.language,
            self.context.fullname.strip())

    @property
    def annotation(self):
        return self.context.description


class ParliamentaryItemToSearchResult(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return "%s - %s" % (self.context.language,
            self.context.short_name)

    @property
    def annotation(self):
        return self.context.body_text


class AttachedFileToSearchResult(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return "%s - %s" % (self.context.language,
            self.context.file_title)

    @property
    def annotation(self):
        return self.context.file_description
    

class GroupToSearchResult(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return "%s - %s" % (self.context.language,
            self.context.short_name)

    @property
    def annotation(self):
        return self.context.description


class ResultListing(object):

    formatter_factory = table.StandaloneFullFormatter

    results = None
    spelling_suggestion = None
    search_time = None
    doc_count = None

    columns = [
        column.GetterColumn(title=_(u"rank"),
            getter=lambda i, f:i.rank),
        column.GetterColumn(title=_(u"type"),
            getter=lambda i, f: i.data.get('object_type', ('',))[0]),
        column.GetterColumn(title=_(u"title"),
            getter=lambda i, f:i.data.get('title', ('',))[0]),
        column.GetterColumn(title=_(u"status"),
            getter=lambda i, f:i.data.get('status', ('',))[0]),
        column.GetterColumn(title=_(u"weight"),
            getter=lambda i, f:i.weight),
        column.GetterColumn(title=_(u"percent"),
            getter=lambda i, f:i.percent),
    ]

    @property
    def search_status(self):
        return "Found %s Results in %s Documents in %0.5f Seconds" % (
            len(self.results), self.doc_count, float(self.search_time))

    def listing(self):
        columns = self.columns
        formatter = self.formatter_factory(self.context, self.request,
                            self.results or (),
                            prefix="results",
                            visible_column_names=[c.name for c in columns],
                            #sort_on = (('name', False)
                            columns=columns
        )
        formatter.cssClasses['table'] = 'listing'
        return formatter()


class Search(forms.common.BaseForm, ResultListing):
    """  basic content search form and results
    """
    template = ViewPageTemplateFile('templates/search.pt')
    form_fields = form.Fields(ISearch)
    #selection_column = columns[0]

    def setUpWidgets(self, ignore_request=False):
        # setup widgets in data entry mode not bound to context
        self.adapters = {}
        self.widgets = form.setUpDataWidgets(self.form_fields, self.prefix,
             self.context, self.request, ignore_request=ignore_request)

    @property
    def doc_count(self):
        return len(self._results)

    @CachedProperty
    def _results(self):
        try:
            results = self.searcher.search(self.query, 0,
                self.searcher.get_doccount())
        except:
            results = []
        return list(results)

    @property
    def results(self):
        return map(lambda x: x.object(), self._results)

    @form.action(label=_(u"Search"))
    def handle_search(self, action, data):
        self.searcher = component.getUtility(interfaces.IIndexSearch)()
        search_term = data[ 'full_text' ]

        if not search_term:
            self.status = _(u"Invalid Query")
            return

        # compose query
        t = time.time()
        lang = self.request.locale.getLocaleID()
        if lang == "en_US": lang = "en"
        if lang == "en_KE": lang = "en-ke"
        text_query = self.searcher.query_parse(search_term)
        lang_query = self.searcher.query_field('language', lang)
        self.query = self.searcher.query_composite(self.searcher.OP_AND, (text_query, lang_query,))
        self.search_time = time.time() - t

        # spelling suggestions
        suggestion = self.searcher.spell_correct(search_term)
        self.spelling_suggestion = (
            search_term != suggestion and suggestion or None)


class Pager(object):
  '''pager for search result page'''
  action_method = 'get'
  items_count = 5

  @property
  def results(self):
      try:
          page = int(self.request.form.get('page', 1))
      except ValueError:
          page = 1
      return map(lambda x: x.object(),
        self._results[self.items_count * (page - 1):self.items_count * page])


  @property
  def pages(self):
      if self.doc_count > self.items_count:
          page_count = self.doc_count / self.items_count + \
              int(bool(self.doc_count % self.items_count))

          def generate_url(x):
              args = dict(self.request.form)
              args.pop('page', None)

              return str(self.request.URL) + '?' + \
                  urllib.urlencode(args) + '&page=%d' % x

          return map(lambda x: {'number':x,
              'url': generate_url(x)}, range(1, page_count + 1))



class PagedSearch(Pager, Search):
  template = ViewPageTemplateFile('templates/pagedsearch.pt')


class AdvancedPagedSearch(PagedSearch):
    template = ViewPageTemplateFile('templates/advanced-pagedsearch.pt')
    form_fields = form.Fields(IAdvancedSearch)
    form_fields["status_date"].custom_widget = SelectDateWidget
    
    def __init__(self, *args):
        super(AdvancedPagedSearch, self).__init__(*args)
        statuses = SimpleVocabulary([])
        indexed_fields = ['all',]
        content_type = self.request.get('form.content_type', '')
        if content_type:
            dotted_name = "bungeni.models.domain.%s" % content_type
            domain_class = resolve.resolve(dotted_name)
            statuses = get_statuses_vocabulary(domain_class)
            f =  IIndexer(domain_class()).fields()
            indexed_fields = indexed_fields + [i for i, fld in f]
            
        self.form_fields += form.Fields(schema.Choice(__name__='status', title=_("Status"),\
                                                       vocabulary=statuses, required=False),\
                                        schema.Choice(__name__='field', title=_('Field'),\
                                                       values = indexed_fields, required=False))

    @form.action(label=_(u"Search"))
    def handle_search(self, action, data):
        self.searcher = component.getUtility(interfaces.IIndexSearch)()
        search_term = data[ 'full_text' ]
        content_type = data['content_type']
        lang = data['language']
        indexed_field = data.get('field', '')
        status = data.get('status', '')
        status_date = data['status_date']
        
        if not lang:
            lang = 'en'

        if not search_term:
            self.status = _(u"Invalid Query")
            return

        # compose query
        t = time.time()
        
        if content_type and indexed_field and indexed_field != 'all':
            text_query = self.searcher.query_field(indexed_field, search_term)
            lang_query = self.searcher.query_field('language', lang)
            self.query = self.searcher.query_composite(self.searcher.OP_AND, (text_query, lang_query,))
        else:
            text_query = self.searcher.query_parse(search_term)
            lang_query = self.searcher.query_field('language', lang)
            self.query = self.searcher.query_composite(self.searcher.OP_AND, (text_query, lang_query,))

        if content_type:
            content_type_query = self.searcher.query_field('object_type', content_type)
            self.query = self.searcher.query_composite(self.searcher.OP_AND, (self.query, content_type_query,))

        if content_type and status:
            status_query = self.searcher.query_field('status', status)
            self.query = self.searcher.query_composite(self.searcher.OP_AND, (self.query, status_query,))

        if status_date:
            status_date_query = self.searcher.query_field('status_date', index.date_value(status_date))
            self.query = self.searcher.query_composite(self.searcher.OP_AND, (self.query, status_date_query,))

        self.search_time = time.time() - t

        # spelling suggestions
        suggestion = self.searcher.spell_correct(search_term)
        self.spelling_suggestion = (
            search_term != suggestion and suggestion or None)

        print self.query
    

class AjaxGetClassStatuses(BrowserView):

    def __call__(self):
        dotted_name = "bungeni.models.domain.%s" % self.request.form.get('dotted_name').split(".")[-1]
        tmp = '<option value="%s">%s</option>'
        try:
            domain_class = resolve.resolve(dotted_name)
            states = get_statuses_vocabulary(domain_class)
            response = [tmp % (state.value, state.title) for state in states]
            return '\n'.join(response)
        except Exception:
            return "ERROR"
        

class AjaxGetClassFields(BrowserView):

    def __call__(self):
        dotted_name = "bungeni.models.domain.%s" % self.request.form.get('dotted_name').split(".")[-1]
        tmp = '<option value="%s">%s</option>'
        try:
            domain_class = resolve.resolve(dotted_name)
            f =  IIndexer(domain_class()).fields()
            response = [tmp % (i, i) for i, fld in f]
            response = [tmp % ('all', 'all'),] + response
            return '\n'.join(response)
        except Exception:
            return "ERROR"


class ConstraintQueryJSON(BrowserView):
    """ Full Text Search w/ Constraint """
    def __call__(self):
        search_term = self.request.form.get('query')
        #if not search_term:
        #    return simplejson.dumps(None)
        self.searcher = component.getUtility(interfaces.IIndexSearch)()
        results = self.query(search_term)
        return simplejson.dumps(results)

    def query(self, search_term, spell_correct=False):
        # result
        d = {}

        # compose and execute query
        t = time.time()
        start, limit = self.getOffsets()
        query = self.composeQuery(search_term)
        sort_key, sort_dir = self.getSort()
        if sort_dir == 'desc':
            sort_key = '-' + sort_key

        results = self.searcher.search(
            query, start, start + limit, sortby=sort_key)

        # prepare results
        d['results'] = self.formatResults(results)
        d['SearchTime'] = time.time() - t
        d['length'] = results.matches_estimated
        d["recordsReturned"] = len(results)
        d['sort'] = sort_key
        d['dir'] = sort_dir
        d['start'] = start
        return d

    def composeQuery(self, search_term):

        if search_term:
            query = self.searcher.query_parse(search_term)
        else:
            query = None

        constraint = self.getConstraintQuery()

        if constraint and query:
            query = self.searcher.query_multweight(query, 3.0)
            if isinstance(constraint, list):
                constraint.insert(0, query)
                query = constraint
            else:
                query = self.searcher.query_composite(
                    self.searcher.OP_AND, (query, constraint)
                )
        elif constraint and not query:
            return constraint
        elif query and not constraint:
            return query
        else:
            raise SyntaxError("invalid constraint query")

        return query

    def getConstraintQuery(self):
        raise NotImplemented

    def getOffsets(self, limit_default=30):
        start = self.request.get('start', 0)
        limit = self.request.get('limit', 25)
        try:
            limit_default = int(limit_default)
            start, limit = int(start), int(limit)
            if not limit:
                limit = limit_default
        except ValueError:
            start, limit = 0, 30
        # xapian end range is not inclusive
        return start, limit + 1

    def getSort(self):
        sort_key = self.request.get('sort', 'title')
        sort_dir = self.request.get('dir', 'asc')
        return sort_key, sort_dir

    def formatResults(self, results):
        r = []
        for i in results:
            r.append(
                dict(rank=i.rank,
                      object_type=i.data.get('object_type'),
                      title=i.data.get('title'),
                      weight=i.weight,
                      percent=i.percent
                )
            )
        return r


class Similar(BrowserView, ResultListing):
    template = ViewPageTemplateFile('templates/similar.pt')

    def update(self):
        resolver = component.getUtility(interfaces.IResolver)

        doc_id = resolver.id(removeSecurityProxy(self.context))

        t = time.time()
        searcher = component.getUtility(interfaces.IIndexSearch)()
        query = searcher.query_similar(doc_id)
        # similarity includes original doc
        # grab first fifteen matching
        self.results = searcher.search(query, 0, 15)
        self.search_time = time.time() - t
        self.doc_count = searcher.get_doccount()

    def render(self):
        return self.template()

    def __call__(self):
        self.update()
        return self.render()


class SearchResultItem(object):

    template = ViewPageTemplateFile('templates/searchresult.pt')

    @property
    def item(self):
       return ISearchResult(self.context)

    def __call__(self):
        return self.template()

