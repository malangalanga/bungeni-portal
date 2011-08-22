from Products.ATContentTypes.browser import nextprevious

class ATFolderNextPrevious(nextprevious.ATFolderNextPrevious):
    """Let a folder act as a next/previous provider. This will be 
    automatically found by the @@plone_nextprevious_view and viewlet.
    """
        
    def buildNextPreviousQuery(self, position, range, sort_order = None):
        sort_on                  = 'getObjPositionInParent'
        
        query                    = {}
        query['sort_on']         = sort_on
        query['sort_limit']      = 1
        query['path']            = dict(query = '/'.join(self.context.getPhysicalPath()),
                                        depth = 1)
                
        # Query the position using a range
        if position == 0:
            query[sort_on]       = 0
        else:
            query[sort_on]       = dict(query = position, range = range)
            
        # Filters on content
        query['is_default_page'] = False
        # This filter is commented out so that all objects (whether folderish or
        # not) will show up in the next/prev navigation
        
        # query['is_folderish']    = False

        # Should I sort in any special way ?
        if sort_order:
            query['sort_order']  = sort_order

        return query
