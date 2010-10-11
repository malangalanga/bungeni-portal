## Script (Python) "alphabetiseContext"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return an alphabetised list of items for the current context
##

import string

items = context.getFolderContents()

alphabets = {}
for x in string.uppercase:
	alphabets[x] = []

for item in items:
	char = item.Title[0].upper()
	if not alphabets.has_key(char):
		continue
	alphabets[char].append(item)

alphabet = [{'letter': x, 'items': alphabets[x]} for x in string.uppercase]

return alphabet

