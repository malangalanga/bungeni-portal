(function($) {
    $('.workflow-status').css('border','1px solid black');
  
    var re_time_range = /(.*) \((\d+):(\d+):\d+-(\d+):(\d+):\d+\)/;
    var re_date_range = /(.*) \((?:(\d+)\/(\d+)\/(\d+)|\?)-(?:(\d+)\/(\d+)\/(\d+)|\?)\)/;

    function _update_tables(selector, data) {
        var calendar = $(selector);
        var old_tables = calendar.find("table");
        var new_tables = $(data).find(selector).find("table");
        
        old_tables.eq(0).replaceWith(new_tables.eq(0));
        old_tables.eq(1).replaceWith(new_tables.eq(1));
    }
    
    $.fn.dragRearrange= function(){
        var helperfn = function(event, ui) {
            var title = ui.children('td.item').children('span:first').text() + 
                             ': ' + ui.children('td.item').children('a').text();
            var helper = $('<div class="helper" />');
            helper.text(title);
            return helper;
        };
        var updatefn = function(event, ui) {
            var ar = $(this).sortable('serialize');
            $("#kss-spinner").show();
            $.post('schedule_order', ar ,function(data, status) {
                $("#kss-spinner").hide();
            });
        };

        $(this).sortable({
            helper: helperfn,
            axis: 'y'
        }).bind( "sortupdate",updatefn);
    };
    
    
  $.fn.clickScheduling = function() {
    var calendar = $('#scheduling-calendar');
    var selector = '#'+calendar.attr('id');
    
    $(this).click(function() {
        var target = $('#scheduling-calendar').find("fieldset");
        var id = $(this).attr('id');
        var next_url = $("a[rel=calendar]").attr('href') + "headless=true";
        if ($(this).is(':checked'))
        {
            var link = target.find("a[rel=schedule-item]");
            var url = link.attr('href');
            // ask for a redirect to the current (updated) calendar
            
            var t =  $(this).parent().parent();                   
            $("#kss-spinner").show();
            $.post(url, {
                    headless: "true",
                        next_url: next_url,
                        item_id: id}, function(data, status) {
                    $("#kss-spinner").hide();
                    if (status == 'success') {
                        _update_tables(selector, data);
                        calendar.bungeniInteractiveSchedule();
                        $("#scheduling-table tbody").dragRearrange();
                        t.addClass("dd-disable");
                        }
                    });
        }            
        else
        {   
            var link = target.find("a[rel=remove-scheduled-item]");
            var url = link.attr('href');
            var t =  $(this).parent().parent();     
            $("#kss-spinner").show();
            $.post(url, {
                       headless: "true",
                       next_url: next_url,
                       item_id: id}, function(data, status) {
			   $("#kss-spinner").hide();
			   if (status == 'success') {
                               _update_tables(selector, data);
                               calendar.bungeniInteractiveSchedule();
                               $("#scheduling-table tbody").dragRearrange();
                               t.removeClass("dd-disable");
                           }
                       });
        }        
		  });
      return this;
  };
  
  $.fn.bungeniInteractiveSchedule = function() {
      $.each($(this), function(i, o) {
		 var calendar = $(this);
		 var selector = '#'+calendar.attr('id');
		 calendar.find("a[rel=edit-scheduling]").hide();
		 var editor = new YAHOO.widget.Editor('editor-textarea', { 
                                                     width: '702px', 
                                                     height: '200px' 
						 }); 
		 editor.on('afterRender', editor.hide);
		 editor.render();
		 var form = calendar.find("editor-form");
		 var dlg = new YAHOO.widget.Dialog('dialog-div', {
						       width:"725px",
						       fixedcenter:true,
						       modal:true,
						       visible:false
						   });
		 function handleSave() {
                     editor.saveHTML();
                     var d = document.getElementById('discussion-full-text-'
                                                     +editor.element_id);
                     d.innerHTML = editor.getEditorHTML();
                     this.submit();
		 }
		 function handleCancel() {
                     this.cancel();
		 }
		 var myButtons = [ { text:"Save", 
				     handler:handleSave },
				   { text:"Cancel", 
				     handler:handleCancel,
				     isDefault:true } ];
		 dlg.cfg.queueProperty("buttons", myButtons);
		 var onSuccess = function(o) {
                     var d = document.getElementById('discussion-full-text-'
                                                     +editor.element_id);
                     //Only show first 100 characters
                     var short_minutes = d.innerHTML.substring(0,100);
                     var display_minutes = "";
                     //Check for newlines
                     var position_of_br = short_minutes.indexOf("<br>");
                     //if there are no newlines, just add dots
                     if (position_of_br == -1){
			 display_minutes = short_minutes+"...";
                     }
                     else{
			 //check for a second newline
			 var second_position_of_br = short_minutes.indexOf(
			     "<br>", position_of_br+4);
			 if (second_position_of_br == -1){
                             display_minutes = short_minutes + "...";
			 }
			 else {
                             display_minutes = 
				 short_minutes.substring(0, 
							 second_position_of_br)
				 +"...";
			 }
                     }    
                     d = document.getElementById("truncated-discussion-"
                                                 +editor.element_id);
                     d.innerHTML = display_minutes;   
		 };
		 var onFailure = function(o) {
                     alert('An error occured when connecting to server.');
		 };
		 dlg.callback.success = onSuccess;
		 dlg.callback.failure = onFailure;
		 dlg.render();
		 dlg.showEvent.subscribe(editor.show, editor, true);
		 dlg.hideEvent.subscribe(editor.hide, editor, true);
		 var discussion = calendar.find('div.full-discussion');
		 $.each(discussion, 
			function(i, o){
			    var a = new Array();
			    a = $(this).attr('id').split("-");
			    var id = a[3];
			    var button_id = "discussion-link-"+id;
			    var btn = new YAHOO.widget.Button(button_id, 
							      {type:"link"});
			    //btn.on("click", dlg.show, dlg, true);
			    var onButtonClick = function (e) {
				var action = calendar.find('#discussion-action-url-'+id).attr('href');
				var dialog_form = dlg.form;
				dialog_form.action = action;
				var html = calendar.find('#discussion-full-text-'+id).html();
				editor.setEditorHTML(html);
				editor.element_id = id;
				dlg.show();
			    };
			    btn.on("click", onButtonClick);
			});
		 var selects = calendar.find('#scheduling-table select.workflow-status');
		 $.each(selects, 
			function(i, o) {
			    var select = $(o);
			    var label = select.siblings(".state-title");
			    var form = select.parents("form").eq(0);
			    select.change(
				function(event) {
				    var selected = select.children().eq(o.selectedIndex);
				    $("#kss-spinner").show();
				    form.ajaxSubmit(
					{dataType: "html",
					 complete: function(xmlHttp){
					     $("#kss-spinner").hide();
					     o.selectedIndex = 0;
					     select.blur();
					     if (xmlHttp.status != 200) {
						 select.attr('disabled', 'disabled');
						 label.text("");
						 var tid = selected.attr('value');
						 top.location.href = form.attr('action') + '?next_url=...&transition=' + tid;
					     }
					     else {
						 var data = xmlHttp.responseXML;
						 var html = $(data.documentElement);
						 var title = html.children().eq(0);
						 var options = html.find("option");
						 select.children().remove();
						 $.each(options, 
							function(j, p) {
							    var option = $("<option />");
							    option.text($(p).text());
							    option.attr('value', $(p).attr('value'));
							    select.append(option);
							});
						 label.text(title.text());
						 if (options.length == 1){
						     select.hide();
						 }
					     }
					 }
					});
				});
			});
		 $("#scheduling-table tbody td.actions a")
		     .click(function() {
				var link = $(this);
				link.blur();
				var mode = null;
				var row = link.parents("tr").eq(0);
				var direction = link.attr("rel");
				var field = link.attr("rev");
				var url = link.attr('href');
				switch (direction) {
				case "move-scheduling-up":
				    mode = 'up';
				    break;
				case "move-scheduling-down":
				    mode = 'down';
				    break;            
				}
				var next_url = $("a[rel=calendar]")
				    .attr('href') + 'headless=false';
				var data = {
				    "headless": "true",
				    "mode": mode,
				    "field": field,
				    "next_url": next_url
				};
				$("#kss-spinner").show();
				$.post(url, data, 
				       function(data, status) {
					   $("#kss-spinner").hide();
					   if (status == 'success') {
					       // manipulate dom to move row up or down
					       switch (direction) {
					       case "move-scheduling-up":
						   var next = row.next();
						   var element = row.prev();
						   if (!element) {return false;}
						   element.insertAfter(row);
						   break;
					       case "move-scheduling-down":
						   element = row.next();
						   if (!element) {return false;}
						   element.insertBefore(row);
						   break;
					       case "delete-scheduling":
						   //row.remove();
						   var calendar = $('#scheduling-calendar')
						   var selector = '#'+calendar.attr('id');
						   _update_tables(selector, data);
						   var old_tables = $('#items-to-be-scheduled-dl');
						   var new_tables = $(data).find('#items-to-be-scheduled-dl');
						   old_tables.eq(0).replaceWith(new_tables.eq(0));
						   $("form.enableFormTabbing,div.enableFormTabbing").each(ploneFormTabbing.initializeForm);
						   $("dl.enableFormTabbing").each(ploneFormTabbing.initializeDL);
						   $(".scheduling-checkbox").clickScheduling();
						   $('#scheduling-calendar').bungeniInteractiveSchedule();
						   break;                  
					       default:
						   return true;
					       }                            
					   } 
					   else {
					       alert(status);
					   }
				       });
				return false;
			    });
	     });
  };

     $.fn.bungeniCalendarInteractivity = function(ajax_navigation) {
	 var calendar = $(this);
	 var selector = '#'+calendar.attr('id');
	 if (ajax_navigation)
	 {
	     calendar.find("thead a.navigation")
		 .click(function() {
			    $("#kss-spinner").show();
			    var href = $(this).attr('href');
			    $.get(href, {}, function(data, status) {
				      $("#kss-spinner").hide();
				      if (status == 'success') {
					  _update_tables(selector, data);
					  calendar.bungeniCalendarInteractivity(
					      ajax_navigation);
				      }
				  });
			    return false;
			});
	 }     
	 return this;
     };
     $.fn.bungeniSafeResize = function() {
	 $.each($(this), 
		function(i, o) {
		    var table = $(o);
		    if (table) {
			var wrapper = $('<div id="calendar-table-resize-wrapper" />');
			table.wrap(wrapper);
			wrapper = table.parents("#calendar-table-resize-wrapper");
			wrapper.resizable({helper: "resize-proxy",
					   handles: "s"
					  });
			wrapper.bind("resizestop", function(event, ui) {
					 var height = wrapper.height();
					 table.css("height", height+"px");
				     });
		    }
		});
	 return this;
     };
     

     function post_workflow_transition(href) {
	 var url_parts = href.split('?');
	 var url = url_parts[0];
	 var params = url_parts[1].split('&'); 
	 var form = $("<form/>").
	     attr("method", "POST").
	     attr("action", url).
	     appendTo(document.body);
	 $.each(params, function(i, o) {
		    var args = o.split('=');
		    var input = $('<input type="hidden" name="'+args[0]+'"/>').
			attr("value", args[1]);
		    input.appendTo(form);
		});
	 form.get(0).submit();
     }
     
     $.fn.bungeniPostWorkflowActionMenuItem = function() {
	 $(this).click(function() {
			   var href = $(this).attr("href");
			   post_workflow_transition(href);
			   return false;
		       });
	 return this;
     };
  
     // when selecting an option on the format "Label
     // (start_time-end_time)", listen to the ``change`` event and
     // update corresponding start- and end time options
     $.fn.bungeniTimeRangeSelect = function(same_day, set_default) {
	 $.each($(this), function(i, o) {
		    var options = $(o).children();
		    var form = $(o).parents("form").eq(0);
		    var start_year = form.find("select[name$=start_date__year]")
			.get(0);
		    var start_month = form.find("select[name$=start_date__month]")
			.get(0);
		    var start_day = form.find("select[name$=start_date__day]")
			.get(0);
		    var start_hour = form.find("select[name$=start_date__hour]")
			.get(0);
		    var start_minute = form.find("select[name$=start_date__minute]")
			.get(0);
		    var start_date = form.find("input[name$=start_date__date]")
			.get(0);
		    var start_time = form.find("input[name$=start_date__time]")
			.get(0);      
		    var end_year = form.find("select[name$=end_date__year]")
			.get(0);
		    var end_month = form.find("select[name$=end_date__month]")
			.get(0);
		    var end_day = form.find("select[name$=end_date__day]")
			.get(0);
		    var end_hour = form.find("select[name$=end_date__hour]")
			.get(0);
		    var end_minute = form.find("select[name$=end_date__minute]")
			.get(0);
		    var end_date = form.find("input[name$=end_date__date]")
			.get(0);
		    var end_time = form.find("input[name$=end_date__time]")
			.get(0); 
		    var handle_date = false;
		    var handle_time = false;
		    if ((start_year && start_month && start_day &&
			 end_year && end_month && end_day) ||(
			     start_date && end_date)) {
			handle_date = true;
		    }
		    if ((start_hour && start_minute &&
			 end_hour && end_minute) ||
			(start_time && end_time)) {
			handle_time = true;
		    }
		    if (!(handle_date || handle_time)){ return;}
		    if (handle_date && same_day) {
			// the year, month and date of the end-time should
			// follow the start-time
			$([end_year, end_month, end_day, end_date]).
			    attr('disabled', 'disabled');
			$(start_year).change(
			    function() {
				end_year.selectedIndex =
				    start_year.selectedIndex; 
			    });
			$(start_month).change(
			    function() {
				end_month.selectedIndex = 
				    start_month.selectedIndex; 
			    });
			$(start_day).change(
			    function() {
				end_day.selectedIndex = start_day.selectedIndex;
			    });
			$(start_date).change(
			    function() {
				end_date.value = start_date.value;});
			form.submit(
			    function() {
				$([end_year, end_month, end_day, end_date]).
				    attr('disabled', '');
			    });
		    }
		    var option_time_matches = [];
		    var option_date_matches = [];
		    $.each(options, function(j, p) {
			       var option = $(p);
			       var text = option.text();
			       var matches = re_time_range.exec(text);
			       if (matches) {
				   option_time_matches.push(matches);
				   option.text(matches[1]);
			       }
			       matches = re_date_range.exec(text); 
			       if (matches) {
				   option_date_matches.push(matches);
				   option.text(matches[1]);
			       }
			   });
		  
		    function convert_matches(matches) {
			for (var k=1; k < matches.length; k++) {
			    var v = matches[k];
			    if (v[0] == '0') {v = v[1];}
			    matches[k] = parseInt(v,10);
			}
		    }
		    
		    function selectitem(select, value) {
			var options = select.options;
			for (var index in options) {
			    var option = options[index];
			    if (option.value == value) {
				select.selectedIndex = parseInt(index, 10);
				break;
			    }
			}
		    }
		    
		    function handle_time_change() {
			var matches = option_time_matches[o.selectedIndex];
			if (!matches) {return;}
			// convert matches to integers
			convert_matches(matches);
			// for each dropdown, change selection
			if (start_hour) {start_hour.selectedIndex = matches[2];}
			if (start_minute) {start_minute.selectedIndex = 
					   matches[3];}
			if (start_time) {start_time.value = matches[2] + ':' + 
					 matches[3];}
			if (end_hour) {end_hour.selectedIndex = matches[4];}
			if (end_minute) {end_minute.selectedIndex = matches[5];}
			if (end_time) {end_time.value = matches[4] + ':' + 
				       matches[5];}        
		    }
		    
		    function handle_date_change() {
			var matches = option_date_matches[o.selectedIndex-1];
			if (!matches) {return;}		
			// for each dropdown, change selection
			if (start_year) {select_item(start_year, matches[2]);}
			if (start_month) {select_item(start_month, matches[3]);}
			if (start_day) {select_item(start_day, matches[4]);}
			if (start_date) {start_date.value=matches[2] + '-' + 
					 matches[3] + '-' + matches[4];}
			if (end_year) {select_item(end_year, matches[5]);}
			if (end_month) {select_item(end_month, matches[6]);}
			if (end_day) {select_item(end_day, matches[7]);}
			if (end_date) {
			    if (matches[5] && matches[6] && matches[7]){ 
				end_date.value=matches[5] + '-' + matches[6] +
				    '-' + matches[7];
			    }
			    else {
				end_date.value='';
			    }
			}        
		    }

		    // setup event handlers
		    if (handle_time) {
			$(o).change(handle_time_change);
			//if (set_default) handle_time_change();
		    }
		    
		    if (handle_date) {
			$(o).change(handle_date_change);
			if (set_default) {handle_date_change();}
		    }
		});
	 return this;
     };
     $.fn.yuiTabView = function(elements) {
	 if (!YAHOO.widget.TabView) {
	     return console.log("Warning: YAHOO.widget.TabView module not loaded.");
	 }
	 var tab_view = new YAHOO.widget.TabView();
	 
	 $.each(elements, function(i, o) {
		    var label = YAHOO.util.Dom.getFirstChild(o);
		    tab_view.addTab(new YAHOO.widget.Tab({
							     labelEl : label, 
							     contentEl : o
							 }));
		});
	 tab_view.appendTo($(this).get(0));
	 tab_view.set('activeTab', tab_view.getTab(0));
	 return this;
     };
  
     $.fn.yuiDataTable = function(context_name, link_url, data_url, fields, 
				  columns, table_id) {
	 if (!YAHOO.widget.DataTable) {
	     return console.log("Warning: YAHOO.widget.DataTable module not loaded.");
	 }
	 var datasource, config;
	 var formatter = function(elCell, oRecord, oColumn, oData) {
	     var object_id = oRecord.getData("object_id");
	     elCell.innerHTML = "<a href=\"" +  link_url + '/' 
		 + object_id + "\">" + oData + "</a>";
	     return this;
	 };
	 YAHOO.widget.DataTable.Formatter[context_name+"Custom"] = formatter;
	 // Setup Datasource for Container Viewlet
	 fields.push({key:"object_id"});
	 datasource = new YAHOO.util.DataSource(data_url);
	 datasource.responseType   = YAHOO.util.DataSource.TYPE_JSON;
	 datasource.responseSchema = {
	     resultsList: "nodes",
	     fields: fields,
	     metaFields: { totalRecords: "length", 
			   sortKey:"sort", 
			   sortDir:"dir", 
			   paginationRecordOffset:"start"}
	 };
	 var fnRequestSent = function(request , callback , tId , caller){
	    jQuery.blockUI({ message:jQuery("#processing_indicatron"),
                             timeout: UNBLOCK_TIMEOUT
                            }); 
	 };
	 datasource.subscribe("requestEvent", fnRequestSent);
	 // filter per column  
	 var get_filter = function(oSelf) {
             var table_columns = oSelf.getColumnSet();
             var qstr = '';
             for (i=0;i<table_columns.keys.length;i++){
		 var input_id = 'input#input-' + table_columns.keys[i].getId();      
		 qstr = qstr + '&filter_' + table_columns.keys[i].getKey() + 
		     '=' + $(input_id).val();
             }   
             return qstr;
	 };  
      
	 // A custom function to translate the js paging request 
	 // into a datasource query    
	 var RequestBuilder = function(oState, oSelf) {
	     // Get states or use defaults
	     oState = oState || {pagination:null, sortedBy:null};
	     var sort = (oState.sortedBy) ? oState.sortedBy.key : "";
	     var dir = (oState.sortedBy && oState.sortedBy.dir === 
			YAHOO.widget.DataTable.CLASS_DESC) ? "desc" : "asc";
	     var startIndex = (oState.pagination) ? 
		 oState.pagination.recordOffset : 0;
	     var results = (oState.pagination) ? 
		 oState.pagination.rowsPerPage : 100;  
	     // Build custom request
	     return  "sort=" + sort +
		 "&dir=" + dir +
		 "&start=" + startIndex +
		 "&limit=" +  results +
		 get_filter(oSelf);
	 };
	 config = {
	     paginator: new YAHOO.widget.Paginator(
		 {rowsPerPage: 25,
		  template: YAHOO.widget.Paginator.TEMPLATE_ROWS_PER_PAGE,
		  rowsPerPageOptions: [10,25,50,100],
		  firstPageLinkLabel : "<<", 
		  lastPageLinkLabel : ">>", 
		  previousPageLinkLabel : "<", 
		  nextPageLinkLabel : ">"
		  //,pageLinks: 5
		 }),
	     initialRequest : 'start=0&limit=25',
	     generateRequest : RequestBuilder, 
	     sortedBy : { dir : YAHOO.widget.DataTable.CLASS_ASC },
	     dynamicData: true, // Enables dynamic server-driven data
	     MSG_SORTASC : "Click to filter and sort ascending",
	     MSG_SORTDESC : "Click to filter and sort descending"
	 }; 
	 table = new YAHOO.widget.DataTable(YAHOO.util.Dom.get(table_id), 
					    columns, datasource, config  ); 
	 table = new YAHOO.widget.DataTable(YAHOO.util.Dom.get(table_id), 
					    columns, datasource, config  ); 
	 var fnRequestReceived = function(request, response){
	     jQuery.unblockUI();
	 };
	 table.subscribe("postRenderEvent", fnRequestReceived);
	 // Update totalRecords on the fly with value from server
	 table.handleDataReturnPayload = function(oRequest,
						  oResponse, oPayload) {
             oPayload = oPayload || {pagination:null, 
				     totalRecords:null};
             oPayload.totalRecords = oResponse.meta.totalRecords;
             oPayload.pagination = oPayload.pagination || {};
             oPayload.pagination.recordOffset = 
		 oResponse.meta.paginationRecordOffset;
             return oPayload;
         };
	 table.fnFilterCallback = {
             success: function(sRequest, oResponse, oPayload){
		 var paginator = table.getState().pagination.paginator;
		 table.onDataReturnInitializeTable(sRequest,
						   oResponse, oPayload);
		 paginator.set('totalRecords', oResponse.meta.totalRecords); 
		 table.render();            
		 paginator.setPage(1);     
             },
             failure: function(sRequest, oResponse, oPayload) {
		 var paginator = table.getState().pagination.paginator;        
		 table.onDataReturnInitializeTable(sRequest, oResponse, 
						   oPayload);
		 table.render();
		 paginator.setPage(1);                            
             }
	 }; 
	 table.fnFilterchange = function(e) {               
             table.getDataSource().sendRequest(
		 RequestBuilder(null,table), table.fnFilterCallback);
             //table.getState().pagination.paginator.setPage(1);
	 };
	 // create the inputs for column filtering
	 var i=0;
	 var table_columns = table.getColumnSet();
	 for (i=0;i<table_columns.keys.length;i++){
             var input = document.createElement('input');
             input.setAttribute('type', 'text');
             input.setAttribute('name', 'filter_' + 
				table_columns.keys[i].getKey());
             input.setAttribute('id', 'input-' + table_columns.keys[i].getId());
             var thEl = table_columns.keys[i].getThEl();  
             thEl.innerHTML = "";
             thEl.appendChild(input);               
	 }
	 table.sortColumn = function(oColumn, sDir) {
	     // Default ascending
	     cDir = "asc";
	     // If already sorted, sort in opposite direction
	     var sorted_by =   this.get("sortedBy");
	     sorted_by = sorted_by || {key:null, dir:null};
	     if(oColumn.key == sorted_by.key) {
		 cDir = (sorted_by.dir === 
			 YAHOO.widget.DataTable.CLASS_ASC || 
			 sorted_by.dir == "") ? "desc" : "asc";
	     }
	     if (sDir == YAHOO.widget.DataTable.CLASS_ASC) {
		 cDir = "asc";
             }
	     else if (sDir == YAHOO.widget.DataTable.CLASS_DESC) {
		 cDir = "desc";
	     } 
	     // Pass in sort values to server request
	     var newRequest = "sort=" + oColumn.key + "&dir=" + 
		 cDir + "&start=0";
	     // Create callback for data request
	     var oCallback = {
		 success: this.onDataReturnInitializeTable,
		 failure: this.onDataReturnInitializeTable,
		 scope: this,
		 argument: {
		     // Pass in sort values so UI can be updated in callback 
		     // function
		     sorting: {
			 key: oColumn.key,
			 dir: (cDir === "asc") ? 
			     YAHOO.widget.DataTable.CLASS_ASC : 
			     YAHOO.widget.DataTable.CLASS_DESC
		     }
		 }
	     };
	     newRequest = newRequest + get_filter(this);                  
	     // Send the request
	     this.getDataSource().sendRequest(newRequest, oCallback);
	 };
	 return true;
     };
  
     $.fn.yuiWorkspaceDataTable = function(context_name, link_url, data_url, 
					   fields, columns, table_id, item_type,
					   status) {
	 if (!YAHOO.widget.DataTable) {
	     return console.log("Warning: YAHOO.widget.DataTable module not loaded.");
	 }
	 var datasource, config;
	 var formatter = function(elCell, oRecord, oColumn, oData) {
	     var object_id = oRecord.getData("object_id");
	     elCell.innerHTML = "<a href=\"" +  link_url + '/' + object_id + 
		 "\">" + oData + "</a>";
	     return this;
	 };
	 YAHOO.widget.DataTable.Formatter[context_name+"Custom"] = formatter;
	 // Setup Datasource for Container Viewlet
	 fields.push({key:"object_id"});
	 datasource = new YAHOO.util.DataSource(data_url);
	 datasource.responseType   = YAHOO.util.DataSource.TYPE_JSON;
	 datasource.responseSchema = {
             resultsList: "nodes",
             fields: fields,
             metaFields: { totalRecords: "length", 
			   sortKey:"sort", 
			   sortDir:"dir", 
			   paginationRecordOffset:"start"}
	 };
	 var fnRequestSent = function(request , callback , tId , caller){
	    jQuery.blockUI({ message:jQuery("#processing_indicatron"),
                             timeout: UNBLOCK_TIMEOUT
                            }); 
	 };
	 datasource.subscribe("requestEvent", fnRequestSent);
	 global_status_var = status;
	 // filter per column  
	 var get_text_filter = function(oSelf) {      
	     var qstr = '&filter_short_name=' + $("#input-yui-col1").val();  
             return qstr;
	 };
	 var get_select_filter = function(oSelf) {    
	     var item_type = $("#input-yui-col3 option:selected");
	     var qstr = '&filter_type=' + item_type.val();  
	     var status = $("#input-yui-col5 option:selected");
	     qstr = qstr+'&filter_status=' + status.val();  
             return qstr;
	 };
	 // A custom function to translate the js paging request 
	 // into a datasource query    
	 var RequestBuilder = function(oState, oSelf) {
	     // Get states or use defaults
	     oState = oState || {pagination:null, sortedBy:null};
	     var sort = (oState.sortedBy) ? oState.sortedBy.key : "";
	     var dir = (oState.sortedBy && oState.sortedBy.dir 
			=== YAHOO.widget.DataTable.CLASS_DESC) ? "desc" : "asc";
	     var startIndex = (oState.pagination) 
		 ? oState.pagination.recordOffset : 0;
	     var results = (oState.pagination) 
		 ? oState.pagination.rowsPerPage : 100;  
	     // Build custom request
	     return  "sort=" + sort +
		 "&dir=" + dir +
		 "&start=" + startIndex +
		 "&limit=" +  results +
		 get_text_filter(oSelf) + get_select_filter(oSelf);
	 }; 
	 config = {
             paginator: new YAHOO.widget.Paginator(
		 {rowsPerPage: 25,
		  template: YAHOO.widget.Paginator.TEMPLATE_ROWS_PER_PAGE,
		  rowsPerPageOptions: [10,25,50,100],
		  firstPageLinkLabel : "<<", 
		  lastPageLinkLabel : ">>", 
		  previousPageLinkLabel : "<", 
		  nextPageLinkLabel : ">"
		  //,pageLinks: 5
		 }),
             initialRequest : 'start=0&limit=25',
             generateRequest : RequestBuilder, 
             sortedBy : { dir : YAHOO.widget.DataTable.CLASS_ASC },
             dynamicData: true, // Enables dynamic server-driven data  
             MSG_SORTASC : "Click to filter and sort ascending",
             MSG_SORTDESC : "Click to filter and sort descending"
	     
	 };
	 table = new YAHOO.widget.DataTable(YAHOO.util.Dom.get(table_id), 
					    columns, datasource, config  ); 
	 var fnRequestReceived = function(request, response){
	     jQuery.unblockUI();
	 };
	 table.subscribe("postRenderEvent", fnRequestReceived);
	 // Update totalRecords on the fly with value from server
	 table.handleDataReturnPayload = function(oRequest, oResponse, oPayload)
	 {
             oPayload = oPayload || {pagination:null, totalRecords:null};
             oPayload.totalRecords = oResponse.meta.totalRecords;
             oPayload.pagination = oPayload.pagination || {};
             oPayload.pagination.recordOffset = 
		 oResponse.meta.paginationRecordOffset;
             return oPayload;
         };
	 table.fnFilterCallback = {
             success: function(sRequest, oResponse, oPayload){
		 var paginator = table.getState().pagination.paginator;
		 table.onDataReturnInitializeTable(sRequest, oResponse, 
						   oPayload);
		 paginator.set('totalRecords', oResponse.meta.totalRecords); 
		 table.render();            
		 paginator.setPage(1);     
             },
             failure: function(sRequest, oResponse, oPayload) {
		 var paginator = table.getState().pagination.paginator;        
		 table.onDataReturnInitializeTable(sRequest, oResponse, 
						   oPayload);
		 table.render();
		 paginator.setPage(1);                            
             }
	 };  
	 table.fnFilterchange = function(e) {               
             table.getDataSource().sendRequest(RequestBuilder(null,table), 
					       table.fnFilterCallback);
             //table.getState().pagination.paginator.setPage(1);
	 };
	 var i=0;
	 var table_columns = table.getColumnSet();
	 var name_column = table_columns.getColumn(0);
	 var input = document.createElement('input');
	 input.setAttribute('type', 'text');
	 input.setAttribute('name', 'filter_' + name_column.getKey());
	 input.setAttribute('id', 'input-' + name_column.getId());
	 var thEl = name_column.getThEl();  
	 thEl.innerHTML = "";
	 thEl.appendChild(input);
	 // Set the html for the item_types
	 var type_column = table_columns.getColumn(1);
	 thEl = type_column.getThEl();  
	 var item_type_select = document.createElement('select');
	 item_type_select.setAttribute('name', 'filter_' 
				       + type_column.getKey());
	 var item_type_select_id = 'input-' + type_column.getId();
	 item_type_select.setAttribute('id', item_type_select_id);
	 for(var prop in item_type) {
             var option = document.createElement('option');
             option.value = prop;
             option.text = item_type[prop];
             try {
		 item_type_select.add(option, null);
             }
             catch(ex) {
		 item_type_select.add(option); // IE only
             }
	 }
	 thEl.innerHTML = "";
	 thEl.appendChild(item_type_select);
	 var status_column = table_columns.getColumn(2);
	 var status_select = document.createElement('select');
	 status_select.setAttribute('type', 'text');
	 status_select.setAttribute('name', 'filter_' + status_column.getKey());
	 var status_select_id = 'input-' + status_column.getId(); 
	 status_select.setAttribute('id',status_select_id);
	 thEl = status_column.getThEl();  
	 i = 0;
	 for(prop in status) {
	     var s = prop.split("+");
	     if (s.length == 1) {
		 var option = document.createElement('option');
		 option.value = prop;
		 option.text = status[prop];
		 try {
		     status_select.add(option, null);
		 }
		 catch(ex) {
		     status_select.add(option); // IE only
		 }
	     }
	 }
	 thEl.innerHTML = "";
	 thEl.appendChild(status_select);
	 var status_date_column = table_columns.getColumn(3);
	 input = document.createElement('input');
	 input.setAttribute('type', 'text');
	 input.setAttribute('name', 'filter_' + status_date_column.getKey());
	 input.setAttribute('id', 'input-' + status_date_column.getId());
	 thEl = status_date_column.getThEl();  
	 thEl.innerHTML = "";
	 thEl.appendChild(input);
	 var item_select = $("#"+item_type_select_id);
	 item_select.change(
	     function(event) {
		 var status_select = $("#"+status_select_id);
		 status_select.empty();
		 var i = 0;
		 var item_select_val = $(this).val();
		 if (item_select_val == ""){
		     for(var prop in global_status_var) { 
			 var s = prop.split("+");
			 if (s.length == 1) {
			     var option = document.createElement('option');
			     option.value = prop;
			     option.text = global_status_var[prop];
			     status_select.append(option);
			 }
		     }
		 }
		 else {
		     var option = document.createElement('option');
		     option.value = "";
		     option.text = "-";
		     status_select.append(option);
		     for(var prop in global_status_var) { 
			 var s = prop.split("+");
			 if (s[0] == item_select_val) {
			     option = document.createElement('option');
			     option.value = s[1];
			     option.text = global_status_var[prop];
			     status_select.append(option);
			 }
		     }
		 }
	     });
	 table.sortColumn = function(oColumn, sDir) {
	     // Default ascending
	     cDir = "asc";
	     // If already sorted, sort in opposite direction
	     var sorted_by =   this.get("sortedBy");
	     sorted_by = sorted_by || {key:null, dir:null};
	     if(oColumn.key == sorted_by.key) {
		 cDir = (sorted_by.dir === YAHOO.widget.DataTable.CLASS_ASC 
			 || sorted_by.dir == "") ? "desc" : "asc";
	     }
	     if (sDir == YAHOO.widget.DataTable.CLASS_ASC) {
		 cDir = "asc";
             }
	     else if (sDir == YAHOO.widget.DataTable.CLASS_DESC) {
		 cDir = "desc";
	     }
	     // Pass in sort values to server request
	     var newRequest = "sort=" + oColumn.key + "&dir=" + cDir 
		 + "&start=0";
	     // Create callback for data request
	     var oCallback = {
		 success: this.onDataReturnInitializeTable,
		 failure: this.onDataReturnInitializeTable,
		 scope: this,
		 argument: {
		     // Pass in sort values so UI can be updated in 
		     // callback function
		     sorting: {
			 key: oColumn.key,
			 dir: (cDir === "asc") ? 
			     YAHOO.widget.DataTable.CLASS_ASC 
			     : YAHOO.widget.DataTable.CLASS_DESC
		     }
		 }
	     };
	     newRequest = newRequest + get_text_filter(this) 
		 + get_select_filter(this);          
	     this.getDataSource().sendRequest(newRequest, oCallback);
	 };
	 return true;
    };
 })(jQuery);
