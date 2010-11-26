window.onload = function(){
    var h = jq('div.depth-1 h1');
    var siblingDivs = h.siblings('div');
    var siblingHR = h.siblings('hr');
    
    h.css({cursor:'pointer', background: 'url(plus.png) 2px 2px no-repeat', paddingLeft: '20px'});
    // hide the siblings
    siblingDivs.hide();
    siblingHR.hide();
    // show them on click
    h.click(function(){
        // get this h1's siblings
        var divs = jq(this).siblings('div');
        var hr = jq(this).siblings('hr');
        
        // get the state of the content
        var state = divs.css('display');
        if(state == 'hidden' || state == 'none'){
                jq(this).css('background-image','url(minus.png)');
                divs.slideDown('fast');
                hr.show();
        }
        else{
                jq(this).css('background-image','url(plus.png)');
                divs.slideUp('fast');
                hr.hide();
        }
    });
    
    
    // table of contents collapsing script
    var toc = jq('td.portlet-toc-item');
    var tocHeading = jq('td.portlet-toc-item div');
    // create the toggle element and add it to the DOM
    var toggle = jq(document.createElement('span'));
    toggle.addClass('togglr');
    toggle.css({cursor:'pointer', background: 'url(plus.png) 2px 2px no-repeat', paddingLeft: '1.35em'});
    tocHeading.prepend(toggle);
    
    jq('td.portlet-toc-item td.portlet-toc-item span.togglr').remove();
    
    // hide the children of each toc.
    jq('td.portlet-toc-item blockquote').css({paddingLeft: '1.5em'}).hide();
    jq('td.portlet-toc-item p').css({paddingLeft: '1.5em'}).hide();
    jq('td.portlet-toc-item td.portlet-toc-item blockquote').css({paddingLeft:'0px'}).show();
    jq('td.portlet-toc-item td.portlet-toc-item p').css({paddingLeft:'0px'}).show();
    
    jq('td.portlet-toc-item span.togglr').click(function(){
        
        // get the objects to be hidden.
        var bq = jq(this).parents('.portlet-toc-item').children('blockquote');
        var p = jq(this).parents('.portlet-toc-item').children('p');
        // get the state of each.
        var bqState = bq.css('display');
        var pState = p.css('display');
        
        if(pState == 'hidden' || pState == 'none' || bqState == 'hidden' || bqState == 'none'){
                jq(this).css('background-image','url(minus.png)');
                p.show();
                bq.show();
        }
        else {
                jq(this).css('background-image','url(plus.png)');
                p.hide();
                bq.hide();
        }
        
    });
    
};
