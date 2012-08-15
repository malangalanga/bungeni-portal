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
