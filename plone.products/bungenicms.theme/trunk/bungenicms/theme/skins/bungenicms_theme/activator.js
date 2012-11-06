window.onload = function(){
jq('.activator').hover(function() {
    jq(this).animate({
        width: '250px'
    }, 350);
}, function() {
    jq(this).animate({
        width: '100px'
    }, 350);
});
};

// Make all external links to open in a new window
$(function() {
    $("a[href^='http']").attr('target','_blank');
});
