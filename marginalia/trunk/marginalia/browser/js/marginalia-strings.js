
/*
 * Languages for annotation Javascript
 */

/*
 * Fetch a localized string
 * This is a function so that it can be replaced with another source of strings if desired
 * (e.g. in a database).  The application uses short English-language strings as keys, so
 * that if the language source is lacking the key can be returned instead.
 */
function getLocalized( s )
{
	return LocalizedAnnotationStrings[ s ];
}

LocalizedAnnotationStrings = {

	
	'public annotation' : 'This comment is public.',
	
	'private annotation' : 'This comment is private.',
		
	'delete annotation button' : 'Delete this comment.',
	
	'annotation link button' : 'Link to another document.',
	
	'annotation link label' : 'Select a document to link to.',
	
	'delete annotation link button' : 'Remove this link.',
	
	'action annotate button' : 'Comment...',
	
	'action insert before button' : 'Insert before...',
	
	'action insert after button' : 'Insert after...',
	
	'action replace button' : 'Replace...',
	
	'action delete button' : 'Delete',
	
	'note note label': 'Comment:',
	
	'note insert label': 'Insert:',
	
	'note insert before label': 'Insert Before:',

	'note insert after label': 'Insert After:',

	'note replace label': 'Replace:',
	
	'note delete label': 'Delete',

	'note annotate label': 'Comment:',	
	
	'browser support of W3C range required for annotation creation' : 'Your browser does not support the W3C range standard, so you cannot create comments.',
	
	'select text to annotate' : 'You must select some text to comment.',
	
	'invalid selection' : 'Selection range is not valid.',
	
	'corrupt XML from service' : 'An attempt to retrieve comments from the server returned corrupt XML data.',
	
	'note too long' : 'Please limit your margin note to 250 characters.',
	
	'quote too long' : 'The passage you have attempted to highlight is too long.  It may not exceed 1000 characters.',
	
	'zero length quote' : 'You must select some text to comment.',
	
	'quote not found' : 'The highlighted passage could not be found',
	
	'create overlapping edits' : 'You may not create overlapping edits',
	
	'warn delete' : 'Delete this comment?',
	
	'blank quote and note' : 'You must enter some note text',

	'blank note' : 'You must enter some note text',

	'invalid text selection' : 'Comments are not allowed on this text selection. Please make a different selection.',
	
	'lang' : 'en'
};
