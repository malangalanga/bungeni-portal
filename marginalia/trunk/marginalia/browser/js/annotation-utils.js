function load() {
  var search_button = document.getElementById('search');
  filterAnnotations(search_button);
}

function show_annotations_on_load()
{
  var serviceRoot = portal_url+'/portal_annotations';
  //var username = 'ploneadmin';
  //var isadmin = 'False';
  var superuser = false;
  if (isadmin == 'True'){
    superuser = true;
  }
  var url = annotatedUrl;
  var restService = '/annotate';
  bungeniMarginaliaInit( username, superuser, url, serviceRoot, restService );
  setTimeout( 'load();', 500);
}
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}

addLoadEvent(show_annotations_on_load);

/*
 * Called when the margin button is clicked to create an annotation.
 * There are two choices for editor:
 * 1. SelectAnnotationNoteEditor - select an edit action
 * 2. BungeniNoteEditor - create a simple margin note
 */
function bungeniClickCreateAnnotation( event, id )
{
  var button = document.getElementById('clear');
  flag = myAnnotations(button);
  if (flag!=true) {
    alert( getLocalized( 'add settings' ) );
    return false
      }
  clickCreateAnnotation(event, id, false);
}

