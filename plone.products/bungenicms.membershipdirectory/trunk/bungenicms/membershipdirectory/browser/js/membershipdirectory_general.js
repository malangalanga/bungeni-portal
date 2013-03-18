jQuery(function($) {
    // "jQuery" is aliased to "$"
    
    // Hide all the elements in the DOM that have a class of "box"
    $('.box').hide();

    $('.clickme').click( function(e) {
        $(this).text(($(this).text() === 'Hide Search Options' ? 'Show Search Options' : 'Hide Search Options')).next('.box').slideToggle();;
        e.preventDefault();
    });
    
    $('#county').change(function(e) {
        //alert($(this).val());
        $.ajax({
            type: 'POST',
            url:'/fetch_constituencies',
            data: {
                'county':$(this).val()
            },
            dataType: 'JSON',
            traditional: true,
            success:function(data){
                constituencies_obj = $.parseJSON(data);
                
                var selectList = "<span>Constituency :</span>";
                selectList += "<select id='constituency' name='constituency'>";
                for (var x = 0; x < constituencies_obj.length; x++) {
                    selectList += "<option value='" + constituencies_obj[x] + "'>" + constituencies_obj[x] + "</option>";
                }
                selectList += "</select>";
                $('#constituencies-container').html(selectList);              
            },
            error:function(errorThrown){
                console.log(errorThrown);
            }
        });
    });

});
