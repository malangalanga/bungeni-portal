from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import getToolByName
from Products.Archetypes.event import ObjectInitializedEvent
import zope.event
import logging
from xml.etree import ElementTree
from plone.memoize.instance import memoize
from cgi import escape

from bungenicms.repository.browser.utils import slugify

def notify_init(obj):
    zope.event.notify(ObjectInitializedEvent(obj))

class ImportInitialStructure(BrowserView):
    vpt = ViewPageTemplateFile("templates/import_initial_structure.pt")
    
    def __call__(self):
        submitted  = self.request.form.get('import.submitted', False)
        if submitted:
            import_file = self.request.form.get('import_file')
            self.importStructure(import_file)
        return self.vpt()

    @property
    def portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow')

    def importStructure(self, import_file):
        tree = ElementTree.parse(import_file)
        for community in tree.getiterator('community'):
            c_title = community.find('name').text
            c_id = slugify(c_title)
            c_desc = community.find('description').text
            
            # create the community
            if c_id not in self.context.objectIds():
                self.context.invokeFactory('RepositoryCommunity',
                                            c_id)
                comm_obj = self.context.get(c_id)
                setattr(comm_obj, 'title', c_title)
                setattr(comm_obj, 'description', c_desc)
                self.portal_workflow.doActionFor(comm_obj, 
                'publish')
                notify_init(comm_obj)
                comm_obj.reindexObject()
                
            # create collections
            for collection in community.getiterator('collection'):
                co_title = collection.find('name').text
                co_id = slugify(co_title)
                co_desc = collection.find('description').text
                parent_community = self.context.get(c_id, None)
                if parent_community:
                    if co_id not in parent_community.objectIds():
                        parent_community.\
                            invokeFactory('RepositoryCollection',
                            co_id)
                        collection_obj = parent_community.get(co_id)
                        setattr(collection_obj, 'title', co_title)
                        setattr(collection_obj, 'description', co_desc)
                        self.portal_workflow.doActionFor(collection_obj,
                        'publish')
                        notify_init(collection_obj)
                        collection_obj.reindexObject()
        return
        
    def sample_xml(self):
        return escape(
        """
        <import_structure>
            <community>
                <name>Community 01 Name</name>
                <description>A description</description>
                <collection>
                    <name>Collection 01 Name</name>
                    <description>A description</description>
                </collection>
                <collection>
                    <name>Collection 02 Name</name>
                    <description>A description</description>
                </collection>
            </community>
            <community>
                <name>Community 02 Name</name>
                <description>A description</description>
                <collection>
                    <name>Collection 01 Name</name>
                    <description>A description</description>
                </collection>
            </community>
        </import_structure/>
        """
        )
