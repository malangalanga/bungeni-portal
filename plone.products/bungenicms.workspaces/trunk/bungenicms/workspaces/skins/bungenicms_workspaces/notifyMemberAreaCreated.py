## Script (Python) "notifyMemberAreaCreated"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Create the member space and associated group spaces
from Products.CMFCore.utils import getToolByName
acl_tool = getToolByName(context, 'acl_users')
pm_tool = getToolByName(context, 'portal_membership')
request = context.REQUEST

from bungenicms.workspaces.content.principal_content import initializeAreas
initializeAreas(pm_tool, acl_tool, request, member_folder_id=context.getId())


