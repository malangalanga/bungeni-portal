function add_transcript(){
    $('#new_transcript').height('200px');
    $('#new_transcript').load('add_transcript', function() {
        $('#transcripts_add_form').append("<div id=transcript_slider>asdfas</div>");
        $("#transcript_slider").slider();
        $('#transcripts_add_form').ajaxForm(function() {
                    $('#video_side_bar').load('display_transcripts');
                    $('#new_transcript').height('10px');
                });
         
     });
}
$(document).ready(function() {
    //$('#new_transcript').hide();
});
