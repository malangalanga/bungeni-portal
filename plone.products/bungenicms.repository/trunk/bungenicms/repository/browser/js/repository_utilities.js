/*
Here we declare utility scripts that are short and belong to no particular file, 
rather than putting them inside the templates.
*/

jQuery(function($) {
    // "jQuery" is aliased to "$"
    jQuery('.fileform').submit( function(e) {
        //e.preventDefault();
        var form = $(this);
        var formUrl = form.attr('action');
        
        $.ajax({
            url     : formUrl + '/load_file',
            type    : 'POST',
            data    : form.serialize(),
            dataType: 'JSON',
            traditional: true,
            success : function( respData ) {
                $('#fileframe').attr('src', $.parseJSON(respData)) // Set the iframe src atrribute
                $("#fileframe").css("display", "block"); // Make the iframe visible
                
                // Set focus on the iframe
                $('html, body').animate({ scrollTop: $('#fileframe').offset().top }, 'slow');
            },
            error : function(errorThrown) {
                console.log(errorThrown);
            }
        });
        return false;
    });

});


/* Toggle Hide and Show of the subject tree widget when adding/editing */
function subject_tree_toggle() {
	var ele = document.getElementById("SubTreeToggleText");
	var text = document.getElementById("SubTreeDisplayText");
	if(ele.style.display == "block") {
    		ele.style.display = "none";
		text.innerHTML = "[+] Show Subject Tree";
  	}
	else {
		ele.style.display = "block";
		text.innerHTML = "[-] Hide Subject Tree";
	}
} 

/* Change the height and width of element */
function autoResizeElement(id){
    var newheight;
    var newwidth;

    if(document.getElementById){
        newheight = document.getElementById(id).contentWindow.document.body.scrollHeight;
        newwidth = document.getElementById(id).contentWindow.document.body.scrollWidth;
    }

    document.getElementById(id).height = (newheight) + "px";
    document.getElementById(id).width = (newwidth) + "px";
}
