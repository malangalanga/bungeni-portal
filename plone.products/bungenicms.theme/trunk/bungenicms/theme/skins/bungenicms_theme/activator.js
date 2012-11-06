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
    var h = window.location.host.toLowerCase();
    $("a[href^='http']:not(a[href^='http://" + h + "']):not(a[href^='http://www." + h + "']), a[href$='.pdf']").attr("target", "_blank");
});
