## Script (Python) "notifyMemberAreaCreated"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Modify new member area
##

# script to publish the member area and create private/public spaces.

from Products.CMFCore.utils import getToolByName
wftool = getToolByName(context, 'portal_workflow')

wftool.doActionFor(context, 'publish')


folders = [["private_folder", "Private folders", 'private'], ["web_pages", "Web pages", 'public']]
for folder in folders:
    context.invokeFactory('Folder', id=folder[0])
    newfolder = getattr(context, folder[0])
    newfolder.setTitle(folder[1])
    if folder[2] =="public":
        wftool.doActionFor(newfolder, 'publish')
        newfolder.update
    newfolder.reindexObject()




