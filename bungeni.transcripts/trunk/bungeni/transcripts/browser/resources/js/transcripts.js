function add_transcript(){
    $('#new_transcript').height('200px');
    $('#new_transcript').load('add_transcript', function() {
        $('#transcripts_add_form').append('<div id="transcript_slider"></div>');
        $("#transcript_slider").slider();
        $('#transcripts_add_form').ajaxForm(function() {
                    $('#video_side_bar').load('display_transcripts');
                    $('#new_transcript').height('10px');
                });
         
     });
}

function edit_transcript(url){
    $('#new_transcript').height('200px');
    $('#new_transcript').load('add_transcript', function() {
        $('#transcripts_add_form').append('<div id="transcript_slider"></div>');
        $("#transcript_slider").slider();
        $('#transcripts_add_form').ajaxForm(function() {
                    $('#video_side_bar').load('display_transcripts');
                    $('#new_transcript').height('10px');
                });
         
     });
}

function play(time){
    $('#embed_vid').get(0).stop();
    $('#embed_vid').
    $('#embed_vid').get(0).play();
}

$(document).ready(function() {
    //$('#testslider').slider();
    $('#video_side_bar').load('display_transcripts');
    $('#form.actions.cancel').click( function(){
            $('#new_transcript').hide();
            alert("asdsdf");
            return false;
        }
    )
});
