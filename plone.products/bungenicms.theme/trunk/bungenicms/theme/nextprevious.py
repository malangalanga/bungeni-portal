from zope.component import getMultiAdapter

from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_inner, aq_parent


class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    def next(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getNextItem(aq_inner(self.context))

    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(aq_inner(self.context))

    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        return INextPreviousProvider(aq_parent(aq_inner(self.context)), None)

    def isViewTemplate(self):
        plone = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return plone.is_view_template()
        
    def trunc(self,s,min_pos=0,max_pos=35,ellipsis=True):
        # Sentinel value -1 returned by String function rfind
        NOT_FOUND = -1
        # Error message for max smaller than min positional error
        ERR_MAXMIN = 'Minimum position cannot be greater than maximum position'
    
        # If the minimum position value is greater than max, throw an exception   
        if max_pos < min_pos:
            raise ValueError(ERR_MAXMIN)
        # Change the ellipsis characters here if you want a true ellipsis
        if ellipsis and len(s) > max_pos:
            suffix = '...'
        else:
            suffix = ''
        # Case 1: Return string if it is shorter (or equal to) than the limit
        length = len(s)
        if length <= max_pos:
            return s + suffix
        else:
            # Case 2: Return it to nearest period if possible
            try:
                end = s.rindex('.',min_pos,max_pos)
            except ValueError:
                # Case 3: Return string to nearest space
                end = s.rfind(' ',min_pos,max_pos)
                if end == NOT_FOUND:
                    end = max_pos
            return s[0:end] + suffix              


class NextPreviousViewlet(ViewletBase, NextPreviousView):
    index = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase, NextPreviousView):
    index = ZopeTwoPageTemplateFile('links.pt')
