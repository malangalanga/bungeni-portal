## Script (Python) "getParentTitleStructure"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return an alphabetised list of items for the current context
##

TRAVERSE_MAX = 3
FINAL_TYPES = [u'HelpCenterReferenceManual', 
			  u'HelpCenterTutorial']

base_title_parts = []

continue_traversal = True
parent_node = context

while continue_traversal:
	parent_node = parent_node.aq_parent
	if parent_node:
		if parent_node.meta_type in FINAL_TYPES:
			continue_traversal = False
		parent_node_title = parent_node.Title()
		base_title_parts.append(parent_node_title)
	else:
		continue_traversal = False
	TRAVERSE_MAX = TRAVERSE_MAX - 1
	if not TRAVERSE_MAX:
		continue_traversal = False

base_title_parts.reverse()


return ' -- '.join(base_title_parts)
