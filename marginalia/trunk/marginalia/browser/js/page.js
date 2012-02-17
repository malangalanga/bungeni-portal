function show_annotations_on_load() 
{
	var serviceRoot = portal_url+'/portal_annotations';
	//var username = '${user/getUserName}';
	var url = annotatedUrl;
	bungeniMarginaliaInit( username, url, serviceRoot );
}
addEventHandler(window, 'load', show_annotations_on_load, window);
		
/*
 * Called when the margin button is clicked to create an annotation.
 * There are two choices for editor:
 * 1. SelectAnnotationNoteEditor - select an edit action
 * 2. BungeniNoteEditor - create a simple margin note
 */
function bungeniClickCreateAnnotation( event, id )
{	
	clickCreateAnnotation( event, id, new SelectActionNoteEditor( ) );
}
