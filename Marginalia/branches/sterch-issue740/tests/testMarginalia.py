#from Products.CMFPlone.tests import PloneTestCase
from Products.PloneTestCase import PloneTestCase
from Products.CMFCore.utils import getToolByName
from Acquisition import Implicit

default_user = PloneTestCase.default_user
portal_name = PloneTestCase.portal_name

PloneTestCase.installProduct("Marginalia")

PloneTestCase.setupPloneSite(products=('Mariginalia',), extension_profiles=('Marginalia:marginalia',))
import ZPublisher

class TestMarginaliaInstall(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.plone = getattr(self.app, portal_name)
        if not self.plone.portal_quickinstaller.isProductInstalled("Marginalia"):
            self.plone.portal_quickinstaller.installProducts(["Marginalia",])

    def testMarginaliaTool(self):        
        self.assert_(hasattr(self.plone, "portal_annotations"),
                     "Annotation Portal Tool missing.")

    def testSiteProperties(self):
        portalProperties = getToolByName(self.plone, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties')
        current = list(siteProperties.getProperty('types_not_searched'))
        self.assert_("Annotations" in current,
                     "'Annotations' missing from types_not_searched portal property.")

    def testAnnotationsWorkflow(self):
        portal_workflow = getToolByName(self.plone, 'portal_workflow')
        self.assert_(portal_workflow._chains_by_type.has_key('Annotations'),
                     "Annotations registered in portal workflow")
        self.assert_(portal_workflow._chains_by_type['Annotations']==(),
                     "Annotations workflow not empty")

    def testNavTreeProperyties(self):
        portalProperties = getToolByName(self.plone, 'portal_properties')        
        navtreeProperties = getattr(portalProperties, 'navtree_properties')
        current = list(navtreeProperties.getProperty('idsNotToList'))
        self.assert_("portal_annotations" in current,
                     "'portal_annotations' missing from idsNotToList navigation tree properties.")
        
    def testCSSRegistry(self):
        STYLESHEETS = ['marginalia.css']
        portal_css = getToolByName(self.plone, 'portal_css')
        for stylesheet in STYLESHEETS:
            self.assert_(stylesheet in portal_css.getResourceIds(),
                         "%s missing from portal_css"%stylesheet)

    def testJavascriptRegistry(self):
        JAVASCRIPTS = ['3rd-party.js', '3rd-party/shortcut.js',
        '3rd-party/cssQuery.js', '3rd-party/cssQuery-level2.js',
        '3rd-party/cssQuery-standard.js', 'prefs.js', 'log.js',
        'html-model.js', 'domutil.js', 'ranges.js',
        'SequenceRange.js', 'XPathRange.js', 'annotation.js',
        'post-micro.js', 'linkable.js', 'marginalia.js',
        'blockmarker-ui.js', 'highlight-ui.js', 'link-ui.js',
        'note-ui.js', 'link-ui-simple.js', 'track-changes.js',
        'RangeInfo.js', 'rest-annotate.js', 'rest-prefs.js',
        'rest-keywords.js', 'marginalia-direct.js',
        'marginalia-config.js', 'marginalia-strings.js',
        'bungeni-annotate.js']
                       
        portal_js = getToolByName(self.plone, 'portal_javascripts')
        for script in JAVASCRIPTS:
            self.assert_(script in portal_js.getResourceIds(),
                         "%s missing from portal_javascript"%script)

class TestMarginaliaAnnotationCreate(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.plone = getattr(self.app, portal_name)
        if not self.plone.portal_quickinstaller.isProductInstalled("Marginalia"):
            self.plone.portal_quickinstaller.installProducts(["Marginalia",])
        self.annotations = getToolByName(self.plone, 'portal_annotations')        

    def testCreateAnnotation(self):
        dict = {'end_block': '/0003', 'access': 'private', 'end_xpath': 'html:p[3]',
                'end_word': 31, 'start_xpath': 'html:p[3]', 'URL': 'http://localhost:8080/marginalia/portal_annotations/annotate',
                'start_word': 26, 'xpath-range': 'html:p[3]/word(26)/char(8);html:p[3]/word(31)/char(7)', 'userid': 'admin', 'end_char': 7, 'start_char': 8, 'note': 'test', 'start_block': '/0003', 'REQUEST_METHOD': 'POST', 'quote_title': 'Annotation demo', 'url': 'http://localhost:8080/marginalia/simple', 'quote': 'A short summary of the content',
                'block-range': '', 'sequence-range': '/3/26.8;/3/31.7', 'link': '',
                'url': 'http://localhost:8080/marginalia/simple'}
        self.annotations.REQUEST.other.update(dict)
        self.annotations.REQUEST.REQUEST_METHOD = "POST"
        annotation_id = self.annotations.annotate()
        self.assert_(hasattr(self.annotations, annotation_id),
                     "Unable to create annotation.")
            
class TestMarginaliaAnnotation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.plone = getattr(self.app, portal_name)
        if not self.plone.portal_quickinstaller.isProductInstalled("Marginalia"):
            self.plone.portal_quickinstaller.installProducts(["Marginalia",])

        self.annotations = getToolByName(self.plone, 'portal_annotations')
        dict = {'end_block': '/0003', 'access': 'private', 'end_xpath': 'html:p[3]',
                'end_word': 31, 'start_xpath': 'html:p[3]', 'URL': 'http://localhost:8080/marginalia/portal_annotations/annotate',
                'start_word': 26, 'xpath-range': 'html:p[3]/word(26)/char(8);html:p[3]/word(31)/char(7)', 'userid': 'admin', 'end_char': 7,
                'start_char': 8, 'note': 'test', 'start_block': '/0003', 'REQUEST_METHOD': 'POST', 'quote_title': 'Annotation demo',
                'url': 'http://localhost:8080/marginalia/simple', 'quote': 'A short summary of the content',
                'block-range': '', 'sequence-range': '/3/26.8;/3/31.7', 'link': ''}
        
        self.annotations.REQUEST.other.update(dict)
        self.annotations.REQUEST.REQUEST_METHOD = "POST"
        self.annotation_id = self.annotations.annotate()
        self.annotation = getattr(self.annotations, self.annotation_id)
        
        #self.annotation_id = self.annotations.invokeFactory(type_name="Annotation", id="annotation_test")
        #self.annotation = getattr(self.annotations, self.annotation_id)
        #self.annotation.update(**dict)
        
    def testAnnotationValues(self):
        self.assert_(self.annotation.getUrl()=='http://localhost:8080/marginalia/simple',
                     "URL not stored in annotation obj.")
        self.assert_(self.annotation.getQuote()=='A short summary of the content',
                     "Quote not stored in annotation obj.")
        self.assert_(self.annotation.getQuote_title()=='Annotation demo',
                     "Quote Title not stored in annotation obj.")
        self.assert_(self.annotation.getStart_block()=='/0003',
                     "Start Block not stored in annotation obj.")
        self.assert_(self.annotation.getStart_xpath()=='html:p[3]',
                     "Start XPath not stored in annotation obj.")
        self.assert_(self.annotation.getEnd_xpath()=='html:p[3]',
                     "Start XPath not stored in annotation obj.")
        self.assert_(self.annotation.getEnd_word()==31,
                     "End Word not stored in annotation obj.")
        self.assert_(self.annotation.getEnd_char()==7,
                     "End Char not stored in annotation obj.")
        self.assert_(self.annotation.getStart_word()==26,
                     "Start Word not stored in annotation obj.")
        self.assert_(self.annotation.getStart_char()==8,
                     "Start Char not stored in annotation obj.")

    def testAnnotationUpdate(self):
        dict = {'id':self.annotation_id, 'note': 'new note', 'link': 'http://modified_link.com'}        
        self.annotations.REQUEST.other.update(dict)
        self.annotations.REQUEST.REQUEST_METHOD = "PUT"
        self.annotation_id = self.annotations.annotate()
        self.assert_(self.annotation.getLink()=='http://modified_link.com',
                     "Link modification failed")
        self.assert_(self.annotation.getNote()=="new note",
                     "Note modification failed")        

    def testFeedUID(self):
        self.assert_(self.annotations.getFeedUID().startswith("tag:"),
                     "Feed UID error.")

    def testCatalog(self):
        query = self.annotations.getSortedFeedEntries(user=default_user, url='http://localhost:8080/marginalia/simple')
        self.assert_(len(query)==1,
                     "Annotation missing from catalog.")
        self.assert_(query[0].getId()==self.annotation_id,
                     "Incorrect annotation object found")

class TestMarginaliaAnnotationDelete(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.plone = getattr(self.app, portal_name)
        if not self.plone.portal_quickinstaller.isProductInstalled("Marginalia"):
            self.plone.portal_quickinstaller.installProducts(["Marginalia",])

        self.annotations = getToolByName(self.plone, 'portal_annotations')
        dict = {'end_block': '/0003', 'access': 'private', 'end_xpath': 'html:p[3]',
                'end_word': 31, 'start_xpath': 'html:p[3]', 'URL': 'http://localhost:8080/marginalia/portal_annotations/annotate',
                'start_word': 26, 'xpath-range': 'html:p[3]/word(26)/char(8);html:p[3]/word(31)/char(7)', 'userid': 'admin', 'end_char': 7,
                'start_char': 8, 'note': 'test', 'start_block': '/0003', 'REQUEST_METHOD': 'POST', 'quote_title': 'Annotation demo',
                'url': 'http://localhost:8080/marginalia/simple', 'quote': 'A short summary of the content',
                'block-range': '', 'sequence-range': '/3/26.8;/3/31.7', 'link': ''}
        
        self.annotations.REQUEST.other.update(dict)
        self.annotations.REQUEST.REQUEST_METHOD = "POST"
        self.annotation_id = self.annotations.annotate()
        self.annotation = getattr(self.annotations, self.annotation_id)

    def testAnnotationDelete(self):
        self.annotations.REQUEST.REQUEST_METHOD = "DELETE"
        self.annotations.REQUEST.QUERY_STRING = "id=%s"%self.annotation_id
        self.annotations.annotate()        
        self.assert_(not hasattr(self.annotations, self.annotation_id),
                     "Annotation delete failed")        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMarginaliaInstall))
    suite.addTest(makeSuite(TestMarginaliaAnnotationCreate))    
    suite.addTest(makeSuite(TestMarginaliaAnnotation))
    suite.addTest(makeSuite(TestMarginaliaAnnotationDelete))        
    return suite

