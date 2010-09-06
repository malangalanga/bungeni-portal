### -*- coding: utf-8 -*- #############################################

import datetime, pytz
import itertools
import os
from zope.datetime import parseDatetimetz
from zope.datetime import DateTimeError
from zope.security.proxy import removeSecurityProxy
from zope.app.form.interfaces import ConversionError, InputErrors
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface.common import idatetime
from zope.app.form.browser.widget import UnicodeDisplayWidget, DisplayWidget
from zope.app.form.browser.textwidgets import TextAreaWidget, FileWidget, TextWidget 
from zope.app.form.browser.itemswidgets import  RadioWidget
from zope.i18n import translate

from zc.resourcelibrary import need
from bungeni.core.i18n import _


path = os.path.split(os.path.abspath(__file__))[0]

class MultiDateTextAreaWidget(TextAreaWidget):
    def _toFieldValue(self, value):
        dates = []
        for token in itertools.chain(*[
            line.split('\n') for line in value.split(',')]):
            token = token.strip()
            if not token:
                continue
            try:
                date = parseDatetimetz(token)
                dates.append(date.date())
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError(
                    _("Invalid date: $value",
                      mapping={'value': token}), v)

        return dates

    def _toFormValue(self, value):
        if value:
            return u"\n".join(date.strftime("%F") for date in value)
        return u""

def CustomRadioWidget( field, request ):
    """ to replace the default combo box widget for a schema.choice field"""
    vocabulary = field.vocabulary
    return RadioWidget( field, vocabulary, request )

class ImageInputWidget(FileWidget):
    """
    render a inputwidget that displays the current
    image and lets you choose to delete, replace or just
    leave the current image as is.
    """
    _missing = u''
    
    
    __call__ = ViewPageTemplateFile('templates/imagewidget.pt')
    
    @property
    def update_action_name(self):
        return self.name + '.up_action'
        
    @property
    def upload_name(self):
        return self.name.replace(".","_") + '_file'
        
    @property
    def imageURL(self):
        return './file-image/%s' % self.context.__name__
        
    def empty_field(self):
        return self._data is None

    def _getFieldInput(self, name):
        return self.request.form.get(name, self._missing)
                
    def _getFormInput(self):
        """extract the input value from the submitted form """
        return (self._getFieldInput(self.update_action_name),
                self._getFieldInput(self.upload_name))
        

    def _toFieldValue( self, (update_action, upload) ):
        """convert the input value to an value suitable for the field.
        check the update_action if we should leave the data alone, delete or replace it"""
        if update_action == u'update':
            if upload is None or upload == '':
                if self._data is None:
                    return self.context.missing_value
                else:
                    raise ConversionError(_('Form upload is not a file object'))
            try:
                seek = upload.seek
                read = upload.read
            except AttributeError, e:
                raise ConversionError(_('Form upload is not a file object'), e)
            else:
                seek(0)
                data = read()
                if data or getattr(upload, 'filename', ''):
                    return data
                else:
                    return self.context.missing_value
        elif update_action == u'delete':
            return None
        elif update_action == u'add':
            if upload is None or upload == '':
                return None
            else:
                try:
                    seek = upload.seek
                    read = upload.read
                except AttributeError, e:
                    raise ConversionError(_('Form upload is not a file object'), e)
                else:
                    seek(0)
                    data = read()
                    if data or getattr(upload, 'filename', ''):
                        return data
                    else:
                        return self.context.missing_value
        else:
            raise NotImplementedError
            return
                
    def hasInput(self):
        """
        determins if the widget widget has changed
        """

        if self.update_action_name in self.request.form:
            action = self.request.form.get(self.update_action_name, self._missing) 
            if action == u'keep':
                return False
            elif action == u'delete':
                return True
            else:
                return self.upload_name  in self.request.form
 

class FileInputWidget(ImageInputWidget):
    fileURL="./download"
    def _toFieldValue( self, (update_action, upload) ):
        value = super(FileInputWidget, self)._toFieldValue((update_action, upload))
        self.request.form['form.file_mimetype']=upload.headers.getheader('Content-Type')
        self.request.form['form.file_name']=upload.filename
        return value

class NoInputWidget(TextWidget):
    def __call__(self):
        return u""

class FileAddWidget(FileInputWidget):
    __call__ = ViewPageTemplateFile('templates/addfilewidget.pt')

class FileEditWidget(FileInputWidget):
    __call__ = ViewPageTemplateFile('templates/editfilewidget.pt')

class FileDisplayWidget(DisplayWidget):
    def __call__(self):
        return u'<a href="./download"> download </a>'


class ImageDisplayWidget(DisplayWidget):
    def __call__(self):
        #from bungeni.ui.utils.url import absoluteURL
        #url = absoluteURL( self.__parent__.context, self.request )
        #return '<img src="' + url + '/file-image/%s" />' % self.context.__name__
        return '<img src="./file-image/%s" />' % self.context.__name__

class HTMLDisplay(UnicodeDisplayWidget):
    
    def __call__( self ):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        return unicode(value)

class RichTextEditor( TextAreaWidget ):
    
    def __call__( self ):
        # require yahoo rich text editor and dependencies
        need('yui-rte')
        need('yui-resize')
        need('yui-button')
        # render default input widget for text
        input_widget = super( RichTextEditor, self).__call__()
        
        # use '_' instead of '.' for js identifiers
        jsid = self.name.replace('.','_')
        
        js_inserts = {'jsid': jsid, 'js_name': self.name}
        
        # attach behavior to default input widget, disable titlebar
        input_widget += u"""
        <script language="javascript">
            options={ height:'300px', 
                      width:'100%%', 
                      dompath:true, 
                      animate:true,
                      focusAtStart:false,
                      markup:'xhtml'};
            var %(jsid)s_editor = new YAHOO.widget.Editor('%(js_name)s', options); 
            YAHOO.util.Event.on(
                %(jsid)s_editor.get('element').form, 
                'submit', 
                function( ev ) { 
                    %(jsid)s_editor.saveHTML(); 
                    }
                );
            %(jsid)s_editor._defaultToolbar.titlebar = false;
            %(jsid)s_editor.on('editorContentLoaded', function() { 
	            resize = new YAHOO.util.Resize(%(jsid)s_editor.get('element_cont').get('element'), { 
	                handles: ['br'], 
	                autoRatio: true, 
	                status: true, 
	                proxy: true, 
	                setSize: false //This is where the magic happens 
	            }); 
	            resize.on('startResize', function() { 
	                this.hide(); 
	                this.set('disabled', true); 
	            },  %(jsid)s_editor, true); 
	            resize.on('resize', function(args) { 
	                var h = args.height; 
	                var th = (this.toolbar.get('element').clientHeight + 2); //It has a 1px border.. 
	                var dh = (this.dompath.clientHeight + 1); //It has a 1px top border.. 
	                var newH = (h - th - dh); 
	                this.set('width', args.width + 'px'); 
	                this.set('height', newH + 'px'); 
	                this.set('disabled', false); 
	                this.show(); 
	            },  %(jsid)s_editor, true); 
	        }); 
            
            
            %(jsid)s_editor.render();
        </script>
        """% js_inserts #(jsid, self.name, jsid, jsid, jsid, jsid)
        
        # return the rendered input widget
        return input_widget
        
class OneTimeEditWidget( TextAreaWidget ):
    """
    a text area that is meant to be used once in between edit.
    when you open an edit form it displays the last entry that
    was made and an empty texarea input that will get stored.
    
    """
    __call__ = ViewPageTemplateFile('templates/one-time-textinput-widget.pt')


class SupplementaryQuestionDisplay(DisplayWidget):
    """
    If a question has a parent i.e it is a supplementary question
    this displays the subject of the parent, else it states that this is an
    initial question
    """
    def __call__( self ):
        if self._data is not None:
            #session = Session()
            #parent = session.query(domain.Question).get(self._data)
            context = removeSecurityProxy (self.context.context)
            parent = context.getParentQuestion()
            return _(u"Supplementary Question to: <br/> %s") % parent
        else:
            return _(u"Initial Question")

class SelectDateWidget( SimpleInputWidget):
    """ A more user freindly date input """
    
    __call__ = ViewPageTemplateFile('templates/selectdatewidget.pt')
        
    _missing = u''
    minYear = None
    maxYear = None

    minYearDelta = 100
    maxYearDelta = 5
    
    js_file = open(path + '/templates/yui-calwidget.js', 'r')
    js_template = js_file.read()
    js_file.close()
    
    
    def __init__(self, *args):
        super(SelectDateWidget, self).__init__(*args)
        need('yui-core')
        need('yui-calendar')
        need('yui-container')
        need('yui-element')
        need('yui-button')
        self.minDate = datetime.date.today() - datetime.timedelta(self.minYearDelta*365)
        self.maxDate = datetime.date.today() + datetime.timedelta(self.maxYearDelta*365)
    
    @property
    def time_zone( self ):
        """ returns something like:  tzinfo=<DstTzInfo 'Africa/Nairobi' LMT+2:27:00 STD> 
        """
        try:
            time_zone = idatetime.ITZInfo(self.request)
        except TypeError:
            time_zone = pytz.UTC
        return time_zone

    @property
    def field_name(self):
        return self.name.replace(".","__")

    def set_min_date(self, date):
        if date:
            if type(date) == datetime.date:
                self.minDate = date
            elif type(date) == datetime.datetime:
                self.minDate = date.date()
            else:
                self.minDate = (datetime.date.today() - 
                            datetime.timedelta(self.minYearDelta*365))
        else:
            self.minDate = (datetime.date.today() - 
                    datetime.timedelta(self.minYearDelta*365))
    def set_max_date(self, date):
        if date:
            if type(date) == datetime.date:
                self.maxDate = date
            elif type(date) == datetime.datetime:
                self.maxDate = date.date()
            else:
                self.maxDate = (datetime.date.today() + 
                        datetime.timedelta(self.maxYearDelta*365))
        else:
            self.maxDate = (datetime.date.today() + 
                    datetime.timedelta(self.maxYearDelta*365))

    def jstr(self, alist):
        return u'["' + u'", "'.join(alist) + u'"]'

    def get_js(self):
        pagedate = datetime.date.today()
        if self.maxDate < pagedate:
            pagedate = self.maxDate
        if (type(self._data) == datetime.date) or (type(self._data) == datetime.datetime):
            pagedate = self._data
        calendar = self.request.locale.dates.calendars['gregorian']
        month = _(u"Choose Month")
        year = _(u"Enter Year")
        submit = _("OK")
        cancel = _(u"Cancel")
        invalidYear = _(u"Please enter a valid year")
        months_short = self.jstr(calendar.getMonthAbbreviations())
        months_long = self.jstr(calendar.getMonthNames()) 
        w_day_1char = self.jstr([dn[:1] for dn in calendar.getDayAbbreviations()]) 
        w_day_short = self.jstr([dn[:2] for dn in calendar.getDayAbbreviations()]) 
        w_day_medium = self.jstr(calendar.getDayAbbreviations())
        w_day_long =  self.jstr(calendar.getDayNames())
        return self.js_template % {'name' : self.field_name,
                    'sel_day': self._day_name,
                    'sel_month' : self._month_name,
                    'sel_year' : self._year_name,
                    'txt_date' : self.date_name,
                    'mindate' : self.minDate.strftime("%m/%d/%Y"),
                    'maxdate' : self.maxDate.strftime("%m/%d/%Y"), 
                    'pagedate' : pagedate.strftime('%m/%Y'),
                    'months_short' : months_short,
                    'months_long' : months_long,
                    'w_day_1char' : w_day_1char,
                    'w_day_short' : w_day_short,
                    'w_day_medium' : w_day_medium,
                    'w_day_long' : w_day_long,
                    'month' : translate(str(month), domain='bungeni.ui', context=self.request),
                    'year' : translate(str(year), domain='bungeni.ui', context=self.request),
                    'submit' : translate(str(submit), domain='bungeni.ui', context=self.request),
                    'cancel' : translate(str(cancel), domain='bungeni.ui', context=self.request),
                    'invalidYear' : translate(str(invalidYear), domain='bungeni.ui', context=self.request)
                     }

    def _days(self):
        dl = []
        for i in range( 1, 32 ):
            dl.append( '%02d' % (i) )
        return dl
        

    def _months(self):
        """ return a dict of month values and names"""
        calendar = self.request.locale.dates.calendars['gregorian']
        i=0
        months = []
        for month in  calendar.getMonthNames():
            i = i+1
            months.append({'num' :  "%02d" % i, 'name': month})
        return months
        
    @property
    def _years(self):
        minYear = self.minYear
        if self.minDate:
            minYear = self.minDate.year
        if minYear is None:
            minYear = datetime.date.today().year - int(self.minYearDelta)
        maxYear = self.maxYear
        if self.maxDate:
            maxYear = self.maxDate.year
        if maxYear is None:
            maxYear = datetime.date.today().year + int(self.maxYearDelta)
        return range( maxYear, minYear-1, -1 )
    
    @property
    def _day_name(self):
        return self.name.replace(".","__") + '__day'

    @property
    def _month_name(self):
        return self.name.replace(".","__") + '__month'

    @property
    def _year_name(self):
        return self.name.replace(".","__") + '__year'
        
    @property
    def date_name(self):
        return self.name.replace(".","__") + '__date'
 
    def hasInput(self):
        """Widgets need to determine whether the request contains an input
        value for them """
        return (self._day_name in self.request.form and 
                self._month_name in self.request.form and 
                self._year_name in self.request.form)

    def _hasPartialInput(self):
        return (self._day_name in self.request.form or 
               self._month_name in self.request.form or 
               self._year_name in self.request.form)
     
    
        
    def _getFormInput(self):
        """extract the input value from the submitted form """
        return (self._getFieldInput(self._day_name),
                self._getFieldInput(self._month_name),
                self._getFieldInput(self._year_name))

                
    def _getFieldInput(self, name):
        return self.request.form.get(name, self._missing)
    
    def _toFieldValue(self, (day, month, year)):
        """convert the input value to an value suitable for the field."""
        if day == self._missing or month == self._missing or year == self._missing:
            if self.required:
                return self.context.missing_value
            else:
                if day + month + year == self._missing:
                    return None
                else:
                    return self.context.missing_value
        else:
            try:
                time_zone = self.time_zone
                return datetime.date(year=int(year), month=int(month), day=int(day), ) #tzinfo=time_zone )
            except ValueError, e:
                raise ConversionError(_(u"Incorrect string data for date"), e)
                
    
    def _toFormValue(self, value):
        """convert a field value to a string that can be inserted into the form"""
        if (value == self.context.missing_value) and self.required:
            d = datetime.date.today()
            return (d.day, d.month, d.year)
        else:
            try:
                return (value.day, value.month, value.year)
            except:
                return( '0', '0', '0')
            
             
    def _getFormValue(self):
        """
        Returns a field value to a string that can be inserted into the form. 
        The difference to _toFormValue is that it takes into account when a form
        has already been submitted but needs to be re-rendered (input error)
        """
        if not self._renderedValueSet():
            if self._hasPartialInput():
                error = self._error
                try:
                    try:
                        value = self.getInputValue()
                    except InputErrors:
                        return self._getFormInput()
                finally:
                    self._error = error
            else:
                if self.required:
                    value = self._getDefault()
                else:
                    value = None
        else:
            value = self._data
        return self._toFormValue(value)

class TextDateWidget(SelectDateWidget):
    """ simple date widget input in a text field """
    __call__ = ViewPageTemplateFile('templates/textdatewidget.pt')
        
    def hasInput(self):
        """Widgets need to determine whether the request contains an input
        value for them """
        return (self.date_name in self.request.form)
        
    def _getFormInput(self):
        """extract the input value from the submitted form """
        return (self._getFieldInput(self.date_name))
        
    def _getFieldInput(self, name):
        return self.request.form.get(name, self._missing)
    
    def _toFieldValue(self, date):
        """convert the input value to an value suitable for the field."""
        if (date == self.context.missing_value) and self.required:
            return self.context.missing_value
        else:
            try:
                return  datetime.datetime.strptime(date,"%Y-%m-%d").date()
            except ValueError, e:
                if date=="":
                    return
                raise ConversionError(_(u"Incorrect string data for date"), e)
            
    
    def _toFormValue(self, value):
        """convert a field value to a string that can be inserted into the form"""
        if (value == self.context.missing_value) and self.required:
            d = datetime.date.today()
            return  datetime.datetime.strftime(d,"%Y-%m-%d")
        else:
            try:
                return datetime.datetime.strftime(value,"%Y-%m-%d")
            except:
                return( '')
            
             
    def _getFormValue(self):
        """
        Returns a field value to a string that can be inserted into the form. 
        The difference to _toFormValue is that it takes into account when a form
        has already been submitted but needs to be re-rendered (input error)
        """
        if not self._renderedValueSet():
            if self.hasInput():
                error = self._error
                try:
                    try:
                        value = self.getInputValue()
                    except InputErrors:
                        return self._getFormInput()
                finally:
                    self._error = error
            else:
                if self.required:
                    value = self._getDefault()
                else:
                    value = None
        else:
            value = self._data
        return self._toFormValue(value)

        
class TextDateTimeWidget(TextDateWidget): 

    __call__ = ViewPageTemplateFile('templates/textdatetimewidget.pt')
    

    @property
    def time_name(self):
        return self.name.replace(".","__") + '__time'
        
    def hasInput(self):
        return (self.date_name in self.request.form and 
                self.time_name in self.request.form)
                    
    def _hasPartialInput(self):
        return (self.date_name in self.request.form or 
                self.time_name in self.request.form)

    def _getFormInput(self):
        """extract the input value from the submitted form """
        return (self._getFieldInput(self.date_name),
                self._getFieldInput(self.time_name))


    def _toFormValue(self, value):
        """convert a field value to a string that can be inserted into the form"""
        if (value == self.context.missing_value) and self.required:
            d = datetime.datetime.now()
            return  (datetime.datetime.strftime(d,"%Y-%m-%d"),
                datetime.datetime.strftime(d,"%H:%M"))
        else:
            try:
                return (datetime.datetime.strftime(value,"%Y-%m-%d"),
                    datetime.datetime.strftime(value,"%H:%M"))
            except:
                return('', '')
                        
    def _toFieldValue(self, (date, time)):
        if (date == self._missing or time == self._missing):
            if self.required:
                return self.context.missing_value
            else:
                if date + time == self._missing:
                    return None
                else:
                    return self.context.missing_value
        else:
            try:
                d = datetime.datetime.strptime(date,"%Y-%m-%d")
                t = datetime.datetime.strptime(time,"%H:%M") 
                return datetime.datetime(year=d.year, month=d.month, 
                    day=d.day, hour=t.hour, minute=t.minute,) 
            except ValueError, e:
                raise ConversionError(_(u"Incorrect string data for date and time"), e)
             
class SelectDateTimeWidget(SelectDateWidget):

    __call__ = ViewPageTemplateFile('templates/selectdatetimewidget.pt')
    
    @property
    def _hour_name(self):
        return self.name.replace(".","__") + '__hour'

    @property
    def _minute_name(self):
        return self.name.replace(".","__") + '__minute'



    def hasInput(self):
        return (super(SelectDateTimeWidget, self).hasInput() and 
                    self._hour_name in self.request.form and 
                    self._minute_name in self.request.form)
    def _hasPartialInput(self):
        return (super(SelectDateTimeWidget, self)._hasPartialInput() or 
            self._hour_name in self.request.form or 
            self._minute_name in self.request.form) 

    def _getFormInput(self):
        return (super(SelectDateTimeWidget, self)._getFormInput() +
                    (self._getFieldInput(self._hour_name),
                    self._getFieldInput(self._minute_name)))

    def _hours(self):
        hl = []
        for i in range( 0, 24 ):
            hl.append( '%02d' % (i) )
        return hl

    def _minutes(self):
        ml = []
        for i in range( 0, 60, 5 ):
            ml.append( '%02d' % (i) )
        return ml

    def _toFormValue(self, value):
        if value == self.context.missing_value and self.required:
            d = datetime.datetime.now()
            return (d.day, d.month, d.year, d.hour, d.minute)
        else:
            try:
                return (value.day, value.month, value.year, 
                    value.hour, value.minute)
            except:
                return ( '0', '0', '0', '0', '0')
                
    def _toFieldValue(self, (day, month, year, hour, minute)):
        if (day == self._missing or month == self._missing or year == self._missing 
                                or hour == self._missing or minute == self._missing):
            if self.required:
                return self.context.missing_value
            else:
                if day + month + year + hour + minute == self._missing:
                    return None
                else:
                    return self.context.missing_value
        else:
            try:
                time_zone = self.time_zone
                return datetime.datetime(year=int(year), month=int(month), 
                    day=int(day), hour=int(hour), minute=int(minute),) 
            except ValueError, e:
                raise ConversionError(_(u"Incorrect string data for date and time"), e)
                            
                           
