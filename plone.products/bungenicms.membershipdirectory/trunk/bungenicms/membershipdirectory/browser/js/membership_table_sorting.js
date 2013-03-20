/* 
   Willmaster Table Sort
   Version 1.0
   July 3, 2011

   Will Bontrager
   http://www.willmaster.com/
   Copyright 2011 Will Bontrager Software, LLC

   This software is provided "AS IS," without any warranty of any kind, without 
   even any implied warranty such as merchantability or fitness for a particular 
   purpose. Will Bontrager Software, LLC grants you a royalty free license to 
   use or modify this software provided this notice appears on all copies. 
*/
//
// One placed to customize - The id value of the table tag.

var TableIDvalue = "memberstable";

//
//////////////////////////////////////
var TableLastSortedColumn = -1;

function SortMemberTable() {
    var sortColumn = parseInt(arguments[0]);
    var type = arguments.length > 1 ? arguments[1] : 'T';
    var dateformat = arguments.length > 2 ? arguments[2] : '';
    var table = document.getElementById("memberstable");
    var tbody = table.getElementsByTagName("tbody")[0];
    var rows = tbody.getElementsByTagName("tr"); 
    var arrayOfRows = new Array();
    type = type.toUpperCase();
    dateformat = dateformat.toLowerCase();
    
    // CRUDE HACK: To allow sorting all rows
	// i starts from 2 to skip table header row
    for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = '';
    }
    
    /////////////// POC test  ////////////////
    var thead = table.getElementsByTagName("thead")[0];
    var thead_rows = thead.getElementsByTagName("tr");        
    var allspans = thead.getElementsByTagName("span")[sortColumn];	
        
    if (allspans.className == 'sortDown') {
	    allspans.innerHTML = '&#x25b2;';
	    allspans.className = 'sortUp';
	
    } else if (allspans.className == 'sortUp') {
        allspans.innerHTML = '&#x25bc;';
        allspans.className = 'sortDown';
    }
    //////////////////////////////
    
    for(var i=0, len=rows.length; i<len; i++) {
	    arrayOfRows[i] = new Object;
	    arrayOfRows[i].oldIndex = i;
	    var celltext = rows[i].getElementsByTagName("td")[sortColumn].innerHTML.replace(/<[^>]*>/g,"");
	    if( type=='D' ) { arrayOfRows[i].value = GetDateSortingKey(dateformat, celltext); }
	    else {
		    var re = type=="N" ? /[^\.\-\+\d]/g : /[^a-zA-Z0-9]/g;
		    arrayOfRows[i].value = celltext.replace(re,"").substr(0,25).toLowerCase();
		}
	}
    if (sortColumn == TableLastSortedColumn) { arrayOfRows.reverse(); }
    else {
	    TableLastSortedColumn = sortColumn;
	    switch(type) {
		    case "N" : arrayOfRows.sort(CompareRowOfNumbers); break;
		    case "D" : arrayOfRows.sort(CompareRowOfNumbers); break;
		    default  : arrayOfRows.sort(CompareRowOfText);
		}
	}
    var newTableBody = document.createElement("tbody");
    for(var i=0, len=arrayOfRows.length; i<len; i++) {
	    newTableBody.appendChild(rows[arrayOfRows[i].oldIndex].cloneNode(true));
	}
    table.replaceChild(newTableBody,tbody);
    
    // CRUDE HACK: To re-paginate after sorting (Should not be here at all)
	/*var pager = new Pager('memberstable', 30, 'pager', 'pageNavPosition'); 
    pager.init(); 
    pager.showPageNav(); 
    pager.showPage(1);*/
                
    alternate(table);
} // function SortMemberTable()

function CompareRowOfText(a,b) {
    var aval = a.value;
    var bval = b.value;
    return( aval == bval ? 0 : (aval > bval ? 1 : -1) );
} // function CompareRowOfText()

function CompareRowOfNumbers(a,b) {
    var aval = /\d/.test(a.value) ? parseFloat(a.value) : 0;
    var bval = /\d/.test(b.value) ? parseFloat(b.value) : 0;
    return( aval == bval ? 0 : (aval > bval ? 1 : -1) );
} // function CompareRowOfNumbers()

function GetDateSortingKey(format, text) {
    if( format.length < 1 ) { return ""; }
    format = format.toLowerCase();
    text = text.toLowerCase();
    text = text.replace(/^[^a-z0-9]*/,"",text);
    text = text.replace(/[^a-z0-9]*$/,"",text); 
    if( text.length < 1 ) { return ""; } 
    text = text.replace(/[^a-z0-9]+/g,",",text); 
    var date = text.split(",");
    
    // Ensure we ALWAYS have a default day if current day empty
    if( date.length < 3 ) { date[2] = date[1]; date[1] = "01"; }
    if( date.length < 3 ) { return ""; }
    var d=0, m=0, y=0;
    
    for( var i=0; i<3; i++ ) {
	    var ts = format.substr(i,1);
	    if( ts == "d" ) { d = date[i]; }
	    else if( ts == "m" ) { m = date[i]; }
	    else if( ts == "y" ) { y = date[i]; }
	}
	
    //if( d < 10 ) { d = "0" + d; }
    //alert("("+text+") " + m + "-" + y)
    
    if( /[a-z]/.test(m) ) {
	    m = m.substr(0,3);
	    switch(m) {
		    case "jan" : m = 1; break;
		    case "feb" : m = 2; break;
		    case "mar" : m = 3; break;
		    case "apr" : m = 4; break;
		    case "may" : m = 5; break;
		    case "jun" : m = 6; break;
		    case "jul" : m = 7; break;
		    case "aug" : m = 8; break;
		    case "sep" : m = 9; break;
		    case "oct" : m = 10; break;
		    case "nov" : m = 11; break;
		    case "dec" : m = 12; break;
		    default    : m = 0;
		}
	}
	
    if( m < 10 ) { m = "0" + m; }
    y = parseInt(y);
    
    if( y < 100 ) { y = parseInt(y) + 2000; }
    
    return "" + String(y) + "" + String(m) + "" + String(d) + "";
} // function GetDateSortingKey()

function alternate(table) {
	// Take object table and get all it's tbodies.
	var tableBodies = table.getElementsByTagName("tbody");
	// Loop through these tbodies
	for (var i = 0; i < tableBodies.length; i++) {
		// Take the tbody, and get all it's rows
		var tableRows = tableBodies[i].getElementsByTagName("tr");
		// Loop through these rows
		// Start at 1 because we want to leave the heading row untouched
		for (var j = 0; j < tableRows.length; j++) {
			// Check if j is even, and apply classes for both possible results
			if ( (j % 2) == 0  ) {
				if ( !(tableRows[j].className.indexOf('odd') == -1) ) {
					tableRows[j].className = tableRows[j].className.replace('odd', 'even');
				} else {
					if ( tableRows[j].className.indexOf('even') == -1 ) {
						tableRows[j].className += " even";
					}
				}
			} else {
				if ( !(tableRows[j].className.indexOf('even') == -1) ) {
					tableRows[j].className = tableRows[j].className.replace('even', 'odd');
				} else {
					if ( tableRows[j].className.indexOf('odd') == -1 ) {
						tableRows[j].className += " odd";
					}
				}
			} 
		}
	}
} // function alternate()


