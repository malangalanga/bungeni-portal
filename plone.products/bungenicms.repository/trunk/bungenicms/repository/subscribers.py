from bungenicms.repository.interfaces import IRepositoryItem
from bungenicms.repository.browser.web import Html

def notifyCreatedRepositoryItem(repositoryitem, event):
    """
    This gets called on IObjectInitializedEvent - which occurs when a new object is created.
    Automatically converts the files attached to this object as PDF
    """ 
    HtmlObj = Html(None, None) 
      
    # Get the item_files for this RepositoryItem 
    repoItem_files = repositoryitem.getItem_files()
    
    # Convert all files to PDF
    for rawfile in repoItem_files:
        fileObjUrl = HtmlObj.convertFileToPdf(repositoryitem, rawfile)
        print "Automatically converted " + rawfile['filename']
