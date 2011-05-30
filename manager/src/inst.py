"""
This module provides bungeni location info.
"""


from java.io import File

separator = File.separator

class Bungeni:
    """
    Class that provides info about bungeni. Where is the installation ? 
    Where are the files located at ?
    """
    
    def __init__(self, path):
        self.root_path = path
        
    def bungeni_main(self):
        """
        Path to bungeni.main
        """
        return self.root_path + separator + separator.join(["src", "bungeni.main"])
    
    def bungeni_custom(self):
        """
        Path to bungeni_custom , perhaps should be modified to get the 
        path from the bungeni_custom.pth file
        """
        return self.root_path + separator + separator.join(["src", "bungeni_custom"])
    
    def ui_xml(self):
        """
        Returns path to ui.xml
        """
        return self.bungeni_custom() + separator + separator.join(["forms", "ui.xml"])
    
    
    def workflow_folder(self):
        return self.bungeni_custom() + separator + "workflows"
    
    def workflow(self, wf_name):
        """
        Returns path to a specific workflow
        """
        import os
        return os.path.join(self.workflow_folder(), wf_name)

    def workflows(self):
        """
        Returns all the workflows in a list
        """
        import os,glob
        return glob.glob(os.path.join(self.workflow_folder(), '*.xml'))
    
    def roles(self):
        import os
        return [os.path.join(self.bungeni_main(), "bungeni", "models", "roles.zcml"),
                os.path.join(self.bungeni_custom(), "sys", "acl", "roles.zcml")]
                             
    
            