from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from bungenicms.membershipdirectory.content.memberprofile import ELECTED_LIST
from bungenicms.membershipdirectory.content.memberprofile import STATUS_LIST
from bungenicms.membershipdirectory.vocabularies import COUNTY_LIST
from bungenicms.membershipdirectory.vocabularies import CONSTITUENCIES_LIST
from bungenicms.membershipdirectory.vocabularies import SPECIAL_INTERESTS_LIST

import json

class Html(BrowserView):

    def queryMembers(self): 
        """
        Generate result items.
        """     
        results = self.generateQuery()
        results = sorted(results)       
        # Do this to exclude the root folder
        for match in results:
            if match.getPath() == '/'.join(self.aq_parent.getPhysicalPath()):
                continue
            yield match  
            
    
    def generateQuery(self):
        """
        Perform a search returning member profiles matching the criteria
        """
        
        query = {}        
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join( self.context.getPhysicalPath() )
        
        query['portal_type'] = ['MemberProfile', 'MembershipDirectory'] #"MemberProfile"
        query['path'] = {'query' : folder_path, 'depth' : 2 }
        query['sort_on'] = "member_full_names" # 'sortable_title' # see indexers.py
        query['sort_order'] = "descending"
      
        for key, value in self.request.form.iteritems():
            if value is not '' and key != 'Search':
               query[key] = value
        
        results = portal_catalog.searchResults(query)
        return results  
        
        
    def getCountyList(self):
        """
        Return a list of counties
        """
        return COUNTY_LIST.items()
        
    
    def getTypeList(self):
        """
        Return a list of types
        """
        return ELECTED_LIST.items()
        
    
    def getStatusList(self):
        """
        Return status list
        """
        return STATUS_LIST.items()
        
        
    def fetch_constituencies(self):
        """
        Return constituencies belonging to a county
        """
        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        county = self.request.form.get('county', '')        
        results = CONSTITUENCIES_LIST[str(county)]        
        return json.dumps(results) 
        
    
    def getInterestVocabValue(self, interestKey):
        """
        Return the corresponding value matching the special interest key
        """
        itemValue = None
        for item in SPECIAL_INTERESTS_LIST.items():
            if item[0] == interestKey:
                itemValue = item[1]
        return itemValue
