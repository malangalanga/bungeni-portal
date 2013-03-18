log = __import__("logging").getLogger("bungeni.ui.redirect")

import datetime

from zope.publisher.browser import BrowserView
from zope import interface
from zope import component
from zope.publisher.interfaces import IPublishTraverse
from zope.annotation.interfaces import IAnnotations

import bungeni.core.globalsettings as prefs
from bungeni.ui.utils import url
from bungeni.models.utils import get_db_user_id


class RedirectToCurrent(BrowserView):
    """Redirect to current.
    
    Goto a url like current/parliamentmembers or current/committees
    and you will be redirected to the apropriate container
    
    """
    interface.implements(IPublishTraverse)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []
        self.currParliament = prefs.getCurrentParliamentId()

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self
        
    def __call__(self):
        """redirect to container"""
        #context = proxy.removeSecurityProxy( self.context )
        response = self.request.response
        root_url = url.absoluteURL(self.context, self.request)
        #response.setHeader('Content-Type', 'application/octect-stream')
        #if len(self.traverse_subpath) != 1:
        #    return
        #fname = self.traverse_subpath[0]
        qstr =  self.request['QUERY_STRING']
        if 'date' not in self.request.form:
            qstr = "%s&date=%s" % (qstr,
                    datetime.date.strftime(datetime.date.today(),'%Y-%m-%d'))
        to_url = root_url + '/parliament/'
        if len(self.traverse_subpath) >= 1:
            # we have a traversal to redirect to
            if self.traverse_subpath[0] == 'parliament':
                to_url = "%s/parliament/obj-%s/%s?%s" % (
                        root_url,
                        self.currParliament,
                        '/'.join(self.traverse_subpath[1:]),
                        qstr)
        return response.redirect(to_url)


class WorkspaceRootRedirect(BrowserView):
    """Redirect logged in users to workspace"""
    def __call__(self):
        request = self.request
        to_url = "/workspace"
        request.response.redirect(to_url)

class _IndexRedirect(BrowserView):
    """Redirect to the named "index" view."""
    index_name = "index"
    def __call__(self):
        request = self.request
        log.warn("%s: %s -> %s" % (
            self.__class__.__name__, request.getURL(), self.index_name))
        request.response.redirect(self.index_name)
class WorkspaceContainerIndexRedirect(_IndexRedirect):
    # !+TRAILING_SLASH(mr, sep-2010) this is still needed?
    index_name = url.set_url_context("pi")
class BusinessIndexRedirect(_IndexRedirect):
    index_name = "whats-on"
class MembersIndexRedirect(_IndexRedirect):
    index_name = "current"
class ArchiveIndexRedirect(_IndexRedirect):
    index_name = "browse"
class AdminIndexRedirect(_IndexRedirect):
    index_name = "content"

class SignatoryReview(BrowserView):
    """Redirect to signatory document workflow page
    """
    def __call__(self):
        request = self.request
        context = self.context
        item_id = context.parliamentary_item_id
        user_id = get_db_user_id()
        signatories = context.signatories
        _filters = {"user_id": user_id}
        _signatories = signatories.query(**_filters)
        if len(_signatories) == 1:
            signatory = _signatories[0]
            _signatory = signatories.get(signatory.signatory_id)
            review_url = "/".join(
                (url.absoluteURL(_signatory, request), u"workflow")
            )
            return request.response.redirect(review_url)
        
        

