from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager import NamedVocabulary
from DateTime import DateTime
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
import datetime
import time
import inspect
import calendar
import json

log = __import__("logging").getLogger("bungenicms.repository.browser")

# Location of file objects in Plone root after conversion using documentviewer
CONVERTED_FILES_FOLDER = "files-folder"


def docViewerInstalled():
    try:
        import collective.documentviewer
        return True
    except:
        return False            
            
class Html(BrowserView):

    def __call__(self):
        if 'form.action.convert' in self.request:
            self.process_document()
        return self.index()
        

    def format_date(self, date_string):
        """
        Format the date i.e. from '1982/09/15 00:00:00 GMT+3' to '15-Sep-1982'
        """
        if len( str(date_string) ) == 0:
            new_day = None
        else:
            the_day, the_time, the_tzone = str(date_string).split(" ")
            day_obj = time.strptime(the_day, "%Y/%m/%d")
            new_day = time.strftime("%d-%b-%Y", day_obj)
        
        return new_day
        
        
    def get_years(self): 
        """
        Get a list of years and return
        """
    
        items = []

        # Get a datetime object
        now = datetime.datetime.now()
        currentYear = now.year
        startYear = 1950
        
        for eachYear in range(startYear, (currentYear + 5), 1):
            items.append( str(eachYear) ) 

        return items

    def get_available_years(self): 
        """
        Get a dynamic list of years from the RepositoryItem objects
        """
        
        items = []    
        query = {}        
        portal_catalog = getToolByName(self, 'portal_catalog')
        
        query['portal_type'] = "RepositoryItem"
        query['path'] = {'query' : '/'.join(self.context.getPhysicalPath()), 'depth' : 2 }
        
        brains = portal_catalog.searchResults(query)
        
        for item in brains:
            year = str(item['item_publication_year']).strip()
            if year not in items:
                items.append( year )
                
        # Sort the years in the least
        items = sorted(items, reverse=True)
        
        return items
        
    def get_month_name(self, month_index):
        """
        Get the month name from the month index e.g. Given a month index of 3,
        we should return March, since it is the third month.
        """
        
        name_of_month = ""
        
        try:
        
            if (month_index is not None) or (month_index is not ""):
                name_of_month = calendar.month_name[int(month_index)]
            else:
                name_of_month = None
        except TypeError:
            print("Argument must be a string or a number, not a Missing.Value")
        
        return name_of_month        
        
    def get_full_date(self, day, month, year):
        """
        Format date and return
        """
        full_date = "0"
        final_date = ""
        
        if (year is not None) and (int(year or 0) is not 0):
            full_date = str(year)
            final_date = datetime.datetime.strptime(full_date,'%Y')
            final_date = final_date.strftime("%Y")
            if (month is not None) and (int(month or 0) is not 0):
                full_date += '-' + str(month)
                final_date = datetime.datetime.strptime(full_date, '%Y-%m')
                final_date = final_date.strftime("%B, %Y")
                if (day is not None) and (int(day or 0) is not 0):
                    full_date += '-' + str(day)
                    try:
                        final_date = datetime.datetime.strptime(full_date, '%Y-%m-%d')
                        final_date = final_date.strftime("%B %d, %Y")
                    except ValueError:
                        final_date = full_date
                       
        return final_date
    
    def get_parliamentary_types(self):
        """
        Fetch the Legislative Types from the vocabulary and return them 
        back as a list
        """
    
        legislative_types = []        
        legislative_vocab = NamedVocabulary('org.bungeni.metadata.vocabularies.parliamentarytypes')
        legislative_terms = legislative_vocab.getDisplayList(self).items()
        
        for term in legislative_terms:
            legislative_types.append( (term[0], term[1]) )
        
        return legislative_types
        
    def get_parliamentary_term(self, val):
        """
        Return legislative type label for a given value
        """     
        vocabulary = NamedVocabulary('org.bungeni.metadata.vocabularies.parliamentarytypes')
        return vocabulary.getVocabularyDict(self)[val][0]    
        
    def get_groups(self): 
        """
        Get groups within the application and return as a list.
        """

        items = []
        
        gtool = getToolByName(self, 'portal_groups')
        for group in gtool.listGroups():
            items.append((group.getId(), group.title_or_id()))

        return items
              

    def get_queryLength(self): 
        """
        Get length of query items.
        """             
        results = self.generateQuery()
        return len(results)
         
        
    def queryItemRepository(self): 
        """
        Generate result items.
        """     
        results = self.generateQuery()
        results = sorted(results, key=lambda b: ( int(self.get_curr_str(b['item_publication_year'])), int(self.get_curr_str(b['item_publication_month'])), int(self.get_curr_str(b['item_publication_day'])) ), reverse=True)       
        # Do this to exclude the root folder
        for match in results:
            if match.getPath() == '/'.join(self.aq_parent.getPhysicalPath()):
                continue
            yield match  
            
    def generateQuery(self):
        """
        Perform a search returning repository items matching the criteria
        """
        
        query = {}        
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join( self.context.getPhysicalPath() )
        
        query['portal_type'] = ['RepositoryItem', 'RepositoryCollection'] #"RepositoryItem"
        query['path'] = {'query' : folder_path, 'depth' : 2 }
        #query['sort_on'] = "item_publication_year"
        #query['sort_order'] = "descending"
      
        for key, value in self.request.form.iteritems():
            if value is not '' and key != 'Search':
               query[key] = value
        
        results = portal_catalog.searchResults(query)
        return results                           
                     
    
    def get_curr_str(self, the_str): 
        """
        Crude hack to ensure we always have a non-empty string.
        """   
        curr_string = ''
        if the_str:
            curr_string = str(the_str)
        else:
            curr_string = str(0)
            
        return curr_string
    
    
    def get_form_data(self):
        """
        Get the form submitted data and return it back to re-populate the form.
        """
        return {
            "SearchableText": self.request.form.get("SearchableText", ""),
            "item_publication_year": self.request.form.get("item_publication_year", ""),
            "legislative_type": self.request.form.get("legislative_type", ""),
        }
        
        
    def load_file(self):
        """
        Return the URL of the file attached to the RepositoryItem as JSON object
        """
        results = self.process_document()
        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        return json.dumps(results)
    
    
    def process_document(self):
        """
        Convert the file to PDF using collective.documentviewer then return the URL
        """             
        filename = self.request.form['filename']
        fileURL = None
        
        # Get the item_files for this RepositoryItem 
        repoItem_files = self.context.getItem_files()
        for rawfile in repoItem_files:
            if rawfile['filename'] == filename:
                fileURL = self.convertFileToPdf(self.context, rawfile)
        
        return fileURL
        
        
    def convertFileToPdf(self, repositoryitem, fileobj):
        """
        Convert a single file to document viewer using collective.documentviewer
        """
        
        # Check that docviewer is installed before processing
        if docViewerInstalled():
                    
            from collective.documentviewer.convert import Converter
            from collective.documentviewer.settings import GlobalSettings
            from zope.app.component.hooks import getSite
            from bungenicms.repository.browser.interfaces import IEnhancedDocumentViewerSchema
            
            context = repositoryitem
            filename = fileobj['filename'] 
            portal_url = getToolByName(context, 'portal_url')() 
            isFileConverted = False
            
            # Where to put in the newly created objects
            # Get the settings from collective.documentviewer
            gsettings = GlobalSettings(getSite())
            gsettings.use_interface = IEnhancedDocumentViewerSchema
            storage_folder = gsettings.folder_location or CONVERTED_FILES_FOLDER # if empty
            plone_root = context.portal_url.getPortalObject()  
            
            container = None           
            if plone_root.hasObject(storage_folder):
                container = plone_root[storage_folder]
                print "files-folder exists. No need to create a new one."
            else:
                plone_root.invokeFactory("Folder", id=storage_folder, title="Files Folder")
                container = plone_root[storage_folder]
                print CONVERTED_FILES_FOLDER + " does NOT exist. Created a new one."
            
            # Make sure the folder is public/published
            try:
                folder_review_state = container.portal_workflow.getInfoFor(container, 'review_state')
                if not folder_review_state == 'published':
                    container.portal_workflow.doActionFor(container, 'publish', comment='published')
            except:
                print "Could not publish: " + str(container.getId) + " already published?"            
            
            
            # Confirm whether the file has been converted using object UID
            uid = None
            for id, item in container.objectItems():
                if context.UID() == "FILE".join( item.UID().split( 'FILE' )[0:1] ):
                    if filename.translate(None, " ?.!/;:-") == item.UID().split("FNIX",1)[1]:
                        print "A file with the same name already exists. No need to re-convert."
                        isFileConverted = True
                        uid = item.UID()
                        break
                        
            if not isFileConverted:
                # Grant user temp managerial permssions to allow doc conversion.                
                sm = getSecurityManager()
                if "Manager" not in sm.getUser().getRoles():
                    tmp_user = BaseUnrestrictedUser(
                        sm.getUser().getId(),'', ['Manager'],'')
                    newSecurityManager(None, tmp_user)                                  
                
                                
                # Set the file object attributes using the format below:
                
                # [parent_UID]FILE[object_uid]FNIX[file_name]
                
                # NOTE: The file-name generation mechanism used here is 
                # used in other parts of the application. Make sure to 
                # change those parts as well when you make change the following two lines.
                new_fname = filename.translate(None, " ?.!/;:-")
                uid = context.UID() + "FILE" + str(DateTime().millis()) + "FNIX" + new_fname
                
                # Try to create the file object
                container.invokeFactory("File", uid, icon=fileobj['icon'])
                obj_newObject = container[uid]
                obj_newObject._setUID( uid )
                obj_newObject.setTitle( fileobj['filename'] )
                obj_newObject.setDescription( "Description of file " + fileobj['filename'] )
                obj_newObject.setFile( fileobj['file'] )
                obj_newObject.setContentType( fileobj['content_type'] )
                obj_newObject.reindexObject()
                
                # Convert the file
                converter = Converter( obj_newObject )
                converter()
                
                print "Done converting RepositoryItem File object."
            
            resultsurl = ("%s/%s/%s/view#document/p1") %(context.portal_url(), storage_folder, uid) 
            return resultsurl
        
        else:
            print "ERROR: collective.documentviewer is not installed. Unable to view file."
            
        return None
