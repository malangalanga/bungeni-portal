/*
* Use this when you have two header rows
*/function MemberPager(tableName, itemsPerPage, pagerName, positionId) {
    this.tableName = tableName;
    this.itemsPerPage = document.getElementById("itemsToShow").value; //itemsPerPage;
    this.currentPage = 1;
    this.pages = 0;
    this.inited = false;
    
    this.pagerName = pagerName;
    this.positionId = positionId;
    
    this.showRecords = function(from, to) {        
        var rows = document.getElementById(tableName).rows;
        // i starts from 2 to skip table header row
        for (var i = 2; i < rows.length; i++) {
            if (i < from || i > to)  
                rows[i].style.display = 'none';
            else
                rows[i].style.display = '';
        }
    }
    
    this.setItemsPerPage = function(numOfItems) {
        this.itemsPerPage = Number(numOfItems);
    }
    
    this.getItemsPerPage = function() {
        return this.itemsPerPage;
    }
    
    this.showPage = function(pageNumber) {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}
    	
    	// FORCE GETTING PAGE ITEMS COUNT
    	this.itemsPerPage = this.getItemsPerPage();

        var oldPageAnchor = document.getElementById('pg'+this.currentPage);
        oldPageAnchor.className = 'pg-normal';
        
        this.currentPage = pageNumber;
        var newPageAnchor = document.getElementById('pg'+this.currentPage);
        newPageAnchor.className = 'pg-selected';
        
        this.showPageNav();
        
        var from = (pageNumber - 1) * Number(this.itemsPerPage) + 2;
        var to = from + Number(this.itemsPerPage) - 1;
        this.showRecords(from, to);
    }   
    
    this.prev = function() {
        if (this.currentPage > 1)
            this.showPage(this.currentPage - 1);
    }
    
    this.next = function() {
        if (this.currentPage < this.pages) {
            this.showPage(this.currentPage + 1);
        }
    }                        
    
    this.init = function() {
        var rows = document.getElementById(tableName).rows;
        var records = (rows.length - 1); 
        this.pages = Math.ceil(records / Number(this.itemsPerPage));
        this.inited = true;
    }
    
    this.init2 = function(obj) { 
        var selectObj = document.getElementById(obj.id);
        var itemsPerPage = selectObj.options[selectObj.selectedIndex].value;
        
        this.currentPage = 1; // Start from page 1
    
        var itemsToShow = document.getElementById("itemsToShow");
        itemsToShow.value = itemsPerPage;
    
        this.itemsPerPage = document.getElementById("itemsToShow").value;
        
        var rows = document.getElementById(this.tableName).rows;
        var records = (rows.length - 1); 
        this.pages = Math.ceil(records / Number(this.itemsPerPage));
        this.inited = true;        
        
        this.showPageNav(); 
        this.showPage(1);
    }

    this.showPageNav = function() {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}
    	var element = document.getElementById(this.positionId);
    	
    	// Only show the PREV link when necessary
    	if (this.currentPage > 1) {
            var pagerHtml = '<span onclick="' + this.pagerName + '.prev();" class="pg-normal"> &#171 Prev </span> | ';
        } else {
            var pagerHtml = '<span>&nbsp;</span>';
        }
    	
    	if (this.pages > 1) {
            for (var page = 1; page <= this.pages; page++) 
                pagerHtml += '<span id="pg' + page + '" class="pg-normal" onclick="' + this.pagerName + '.showPage(' + page + ');">' + page + '</span> | ';
        }
            
        // Only show the NEXT link when necessary
        if (this.currentPage < this.pages) {
            pagerHtml += '<span onclick="' + this.pagerName+'.next();" class="pg-normal"> Next &#187;</span>';            
        } else {
            pagerHtml += '<span>&nbsp;</span>';
        }             
        
        element.innerHTML = pagerHtml;
        
        if (this.currentPage != null && this.currentPage != 'undefined') {
            var newPageAnchor = document.getElementById('pg'+this.currentPage);
            newPageAnchor.className = 'pg-selected';
        } else {
            var newPageAnchor = document.getElementById('pg1');
            newPageAnchor.className = 'pg-selected';
        }
    }
}

/*
* Use this when you have no header rows
*/
function PagerNoHeader(tableName, itemsPerPage, pagerName, positionId) {
    this.tableName = tableName;
    this.itemsPerPage = itemsPerPage;
    this.currentPage = 1;
    this.pages = 0;
    this.inited = false;
    
    this.pagerName = pagerName;
    this.positionId = positionId;
    
    this.showRecords = function(from, to) {        
        var rows = document.getElementById(tableName).rows;
        // i starts from 1 since we have no table header row
        for (var i = 0; i < rows.length; i++) {
            if (i < from || i > to)  
                rows[i].style.display = 'none';
            else
                rows[i].style.display = '';
        }
    }
    
    this.showPage = function(pageNumber) {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}    	

        var oldPageAnchor = document.getElementById('pg'+this.currentPage);
        oldPageAnchor.className = 'pg-normal';       
        
        this.currentPage = pageNumber;
        var newPageAnchor = document.getElementById('pg'+this.currentPage);
        newPageAnchor.className = 'pg-selected';
        
        this.showPageNav();
        
        var from = (pageNumber - 1) * Number(itemsPerPage);// + 1;
        var to = from + Number(itemsPerPage) - 1;
        this.showRecords(from, to);
        
    }   
    
    this.prev = function() {
        if (this.currentPage > 1)
            this.showPage(this.currentPage - 1);
    }
    
    this.next = function() {
        if (this.currentPage < this.pages) {
            this.showPage(this.currentPage + 1);
        }
    }                        
    
    this.init = function() {
        var rows = document.getElementById(tableName).rows;
        var records = (rows.length - 1); 
        this.pages = Math.ceil(records / itemsPerPage);
        this.inited = true;
    }

    this.showPageNav = function() {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}
    	var element = document.getElementById(this.positionId);       
    	
    	// Only show the PREV link when necessary
    	if (this.currentPage > 1) {
            var pagerHtml = '<span onclick="' + this.pagerName + '.prev();" class="pg-normal"> &#171 Prev </span> | ';
        } else {
            var pagerHtml = '<span>&nbsp;</span>';
        }
        
        for (var page = 1; page <= this.pages; page++) 
            pagerHtml += '<span id="pg' + page + '" class="pg-normal" onclick="' + this.pagerName + '.showPage(' + page + ');">' + page + '</span> | ';
        
        // Only show the NEXT link when necessary
        if (this.currentPage < this.pages) {
            pagerHtml += '<span onclick="'+this.pagerName+'.next();" class="pg-normal"> Next &#187;</span>';            
        } else {
            pagerHtml += '<span>&nbsp;</span>';
        }  
                
        element.innerHTML = pagerHtml;
        
        if (this.currentPage != null && this.currentPage != 'undefined') {
            var newPageAnchor = document.getElementById('pg'+this.currentPage);
            newPageAnchor.className = 'pg-selected';
        } else {
            var newPageAnchor = document.getElementById('pg1');
            newPageAnchor.className = 'pg-selected';
        }
        
        
    }
}

/*
* Use this when you have no header rows and have more than one table that needs 
* to be paginated.
*/
function PagerNoHeader2(tableName, itemsPerPage, pagerName, positionId) {
    this.tableName = tableName;
    this.itemsPerPage = itemsPerPage;
    this.currentPage = 1;
    this.pages = 0;
    this.inited = false;
    
    this.pagerName = pagerName;
    this.positionId = positionId;
    
    this.showRecords = function(from, to) {        
        var rows = document.getElementById(tableName).rows;
        // i starts from 1 since we have no table header row
        for (var i = 0; i < rows.length; i++) {
            if (i < from || i > to)  
                rows[i].style.display = 'none';
            else
                rows[i].style.display = '';
        }
        
    }
    
    this.showPage = function(pageNumber) {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}   	

        var oldPageAnchor = document.getElementById('pgd'+this.currentPage);
        oldPageAnchor.className = 'pg-normal';       
        
        this.currentPage = pageNumber;
        var newPageAnchor = document.getElementById('pgd'+this.currentPage);
        newPageAnchor.className = 'pg-selected';  
        
        this.showPageNav();      
        
        var from = (pageNumber - 1) * Number(itemsPerPage);// + 1;
        var to = from + Number(itemsPerPage) - 1;        
        
        this.showRecords(from, to);
    }   
    
    this.prev = function() {        
        if (this.currentPage > 1) {
            this.showPage(this.currentPage - 1);
        }        
    }
    
    this.next = function() {        
        if (this.currentPage < this.pages) {
            this.showPage(this.currentPage + 1);
        }        
    }                        
    
    this.init = function() {
        var rows = document.getElementById(tableName).rows;
        var records = (rows.length - 1); 
        this.pages = Math.ceil(records / itemsPerPage);
        this.inited = true;
    }

    this.showPageNav = function() {
    	if (! this.inited) {
    		alert("not inited");
    		return;
    	}
    	
    	//this.pagerName = pagerName;
        //this.positionId = positionId;
    	
    	var element = document.getElementById(this.positionId);
    	
    	// Only show the PREV link when necessary
    	if (this.currentPage > 1) {
            var pagerHtml = '<span onclick="' + this.pagerName + '.prev();" class="pg-normal"> &#171 Prev </span> | ';
        } else {
            var pagerHtml = '<span>&nbsp;</span>';
        }
    	
        for (var page = 1; page <= this.pages; page++) 
            pagerHtml += '<span id="pgd' + page + '" class="pg-normal" onclick="' + this.pagerName + '.showPage(' + page + ');">' + page + '</span> | ';
            
        // Only show the NEXT link when necessary
        if (this.currentPage < this.pages) {
            pagerHtml += '<span onclick="'+this.pagerName+'.next();" class="pg-normal"> Next &#187;</span>';            
        } else {
            pagerHtml += '<span>&nbsp;</span>';
        }
        
        element.innerHTML = pagerHtml;
        
        if (this.currentPage != null && this.currentPage != 'undefined') {
            var newPageAnchor = document.getElementById('pgd'+this.currentPage);
            newPageAnchor.className = 'pg-selected';
        } else {
            var newPageAnchor = document.getElementById('pgd1');
            newPageAnchor.className = 'pg-selected';
        } 
    }
}
