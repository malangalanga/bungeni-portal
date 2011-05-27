## Controller Python Script "login_next"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Login next actions
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import ZTUtils


REQUEST = context.REQUEST

util = context.plone_utils
membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    util.addPortalMessage(_(u'Login failed'), 'error')
    return state.set(status='failure')   

came_from = context.portal_url()
return REQUEST.RESPONSE.redirect(came_from)

state.set(came_from=came_from)

return state
