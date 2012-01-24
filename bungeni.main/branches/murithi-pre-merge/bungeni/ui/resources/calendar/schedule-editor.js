/*
 * This module instatiates a datatable for items in sitting. We also render
 * a panel with items available for scheduling.
 * 
 */

(function() {
    var Dom = YAHOO.util.Dom;
    var Event = YAHOO.util.Event;
    var Y$ = YAHOO.util.Selector;
    var YCM = YAHOO.util.Connect;
    var YJSON = YAHOO.lang.JSON;
    var itemsDataTable = null;
    var itemsDataSource = null;
    var schedulerActions = null;
    var schedulerLayout = null;
    var available_items_loaded = false;
    var saveDialog = null;
    var savingDialog = null;
    var deleteDialog = null;
    var localPermissions = null;
    var ITEM_SELECT_ROW_COLUMN = "item_select_row"
    var ITEM_TYPE_COLUMN = "item_type";
    var ITEM_MOVER_COLUMN = "item_mover"
    var ITEM_MOVE_UP_COLUMN = "item_move_up";
    var ITEM_MOVE_DOWN_COLUMN = "item_move_down";
    var ITEM_DELETE_COLUMN = "item_delete";
    var CHECK_BOX_SELECTOR = "input[type=checkbox]"
    var DIALOG_CONFIG = {
            width: "auto",
            fixedcenter: true,
            modal: true,
            visible: false,
            draggable: false,
            underlay: "none",
    }
    var HIGHLIGHT_TYPES = ["heading", "text"];
    var HIGHLIGHT_TYPES_CSS_CLASS = "schedule-text-item";

    /*utilities*/
    /**
     * @function wrapText
     * @description returns text as html wrapped in el tags
     */
    var wrapText = function(text, el){
        var _el = el || "em";
        return "<" + _el + ">" + text + "</" + _el + ">";
    }

    /**
     * Custom method of added to data table to refresh data
     **/
    YAHOO.widget.DataTable.prototype.refresh = function(params) {
        var dataSource = this.getDataSource();
        var data_url = null;
        if (params != undefined){
            var data_params = new Array()
            for (filter in params){
                data_params.push([filter, params[filter]].join("="));
            }
            data_url = "&" + data_params.join("&");
        }
        dataSource.sendRequest(
                data_url,
                {
                    success: this.onDataReturnInitializeTable,
                    failure: this.onDataReturnInitializeTable,
                    scope: this
                }
        );
    };

    // custom column formatters
    /**
     * @method itemSelectorFormatter
     * @description renders checkboxes to select items on the schedule
     */
    var itemSelectFormatter = function(el, record, column, data){
        index = this.getTrIndex(record) + 1;
        el.innerHTML = "<input type='checkbox' name='rec-sel-" + index + "'/>"
    }

    /**
     * @method itemTitleFormatter
     * @description renders title, emphasized text for titles and italicized
     * text for text records
     */
     var itemTitleFormatter = function(el, record, column, data){
         rec_data = record.getData();
         if(rec_data.item_type == scheduler_globals.types.HEADING){
             el.innerHTML = "<span style='text-align:center;display:block;'><strong>" + rec_data.item_title + "</strong></spam>";
         }else if(rec_data.item_type == scheduler_globals.types.TEXT){
             el.innerHTML = wrapText(rec_data.item_title);
         }else{
             el.innerHTML = rec_data.item_title + "<em><span style='display:block;'>Moved by: " + rec_data.item_mover + "</span></em>";
         }
     }

    /**
     * @method itemTypeFormatter
     * @description render item type in reduced form
     */
     var itemTypeFormatter = function(el, record, column, data){
         el.innerHTML = "<span style='font-size:10px;'>" + record.getData()[ITEM_TYPE_COLUMN] + "</span>";
     }

    /**
     * @method itemMoveFormatter
     * @description renders controls to move scheduled items up/down the
     * schedule depending on direction
     */
    var itemMoveFormatter = function(el, record, column, data, dir, table){
        var move_markup = "";
        var index = table.getTrIndex(record) + 1;
        var last_row = table.getRecordSet().getLength();
        var dir_char = (dir=="up")?"&uarr;":"&darr;"

        if (!(((index == 1) && (dir=="up")) || 
            ((index == last_row) && (dir=="down"))
        )){
            move_markup = "<span id='up'>" + dir_char + "</span>";
        }
        el.innerHTML = move_markup;
    }
    var itemMoveUpFormatter = function(el, record, column, data){
        itemMoveFormatter(el, record, column, data, "up", this);
    }
    var itemMoveDownFormatter = function(el, record, column, data){
        itemMoveFormatter(el, record, column, data, "down", this);
    }

    var itemDeleteFormatter = function(el, record, column, data){
        el.innerHTML = "<span><strong>X</strong></span>";
    }

    // scheduler handlers for various events
    /**
     * @function addTextToSchedule
     * @description Adds a text record row to the schedule and updates dynamic
     * cells of the current row.
     * 
     */
    var addTextToSchedule = function(event, item_type){
        var currentItem = schedulerActions.currentItem;
        var new_record_index = (
            (currentItem && itemsDataTable.getTrIndex(currentItem) + 1) || 0
        );
        itemsDataTable.addRow(
            { 
                item_title: scheduler_globals.initial_editor_text, 
                item_type: (item_type || "text")
            }, 
            new_record_index
        );
        var new_record = itemsDataTable.getRecord(
            itemsDataTable.getTrEl(new_record_index)
        );
        var target_columns = [
            itemsDataTable.getColumn(ITEM_MOVE_UP_COLUMN),
            itemsDataTable.getColumn(ITEM_MOVE_DOWN_COLUMN),
        ]
        itemsDataTable.unselectAllRows();
        itemsDataTable.selectRow(new_record);
        var updated_record = itemsDataTable.getRecord(
            (new_record_index - 1 )
        );
        for (col_index=0; col_index<=(target_columns.length); col_index++){
            itemsDataTable.updateCell(updated_record, 
                target_columns[col_index],
                updated_record.getData()
            );
        }
        //show cell editor
        itemsDataTable.cancelCellEditor();
        selected_index = itemsDataTable.getSelectedRows()[0];
        selected_row = itemsDataTable.getTrEl(selected_index);
        oRecord = itemsDataTable.getRecord(selected_index);
        oColumn = itemsDataTable.getColumn("item_title");
        Event.stopEvent(event);
        itemsDataTable.showCellEditor(
            itemsDataTable.getCell({ record: oRecord, column: oColumn })
        );
    }
    
    /**
     * @method addHeadingToSchedule
     * @description add a heading record to schedule
     */
     var addHeadingToSchedule = function(event){
         addTextToSchedule(event, "heading");
     }
    
    /**
     * @method showCellEditor
     * @description displays an editor to modify text records on the schedule
     */
    var showCellEditorHandler = function(event){
        var target = Event.getTarget(event);
        var record = this.getRecord(target);
        if (record.getData().item_type == "text"){
            this.onEventShowCellEditor(event);
        }
    }

    /**
     * @method reorderRow
     * @description moves an entry up or down the schedule when the up or
     * down selectors are pushed
     */
    var reorderRow = function(args){
        var target_column = this.getColumn(args.target);
        if ([ITEM_MOVE_UP_COLUMN, ITEM_MOVE_DOWN_COLUMN].indexOf(
                target_column.field
            ) >= 0
        ){
            var target_record = this.getRecord(args.target);
            var target_index = this.getTrIndex(target_record);
            var record_count = this.getRecordSet().getLength();
            var swap_rows = [];
            if (target_column.field == ITEM_MOVE_UP_COLUMN){
                if (target_index!=0){
                    swap_rows = [target_index, (target_index - 1)]
                }
            }else{
                if (target_index != (record_count-1)){
                    swap_rows = [target_index, (target_index + 1)]
                }
            }
            
            if (swap_rows.length == 2){
                var data_0 = this.getRecord(swap_rows[0]).getData();
                var data_1 = this.getRecord(swap_rows[1]).getData();
                this.updateRow(swap_rows[0], data_1)
                this.updateRow(swap_rows[1], data_0)
            }
        }
    }

    /**
     * @method removeSelectedRow
     * @description deletes a row and record from the schedule. Displays
     * a dialog to confirm intention before deleting item
     * */
    var removeSelectedRow = function(args){
        var target_row = itemsDataTable.getSelectedRows()[0];
        var target_index = itemsDataTable.getTrIndex(itemsDataTable.getTrEl(target_row));
        deleteDialog.show();
        deleteDialog.bringToTop();
    }

    /**
     * @method highlightTypedRows
     * @description applies additional css class to certain scheduled types
     */
    var highlightTypedRows = function(oArgs){
        if (oArgs == undefined){
            var record_set = this.getRecordSet().getRecords();
            for(record_index in record_set){
                record = record_set[record_index];
                if (HIGHLIGHT_TYPES.indexOf(record.getData().item_type) >= 0){
                    row = this.getTrEl(record);
                    Dom.addClass(row, HIGHLIGHT_TYPES_CSS_CLASS);
                }
            }
        }else{
            Dom.addClass(this.getTrEl(oArgs.record), HIGHLIGHT_TYPES_CSS_CLASS);
        }
    }
    
    /**
     *@method initShowSchedulerControls
     * @description show scheduler controls if initial recordset is empty
     **/
     var initShowSchedulerControls = function(oArgs){
         if (this.getRecordSet().getLength() == 0){
             showSchedulerControls({record:null, el:this.getTheadEl()});
         }
     }
    /**

     *@method hideSchedulerControls
     * @description hide scheduler controls after adding of first item
     **/
     var hideSchedulerControls = function(oArgs){
         if (this.getRecordSet().getLength() == 1 && 
            schedulerActions.currentItem == null
         ){
             schedulerActions.hide();
         }
     }
     

    /**
     * @method showSchedulerControls
     * @description displays a contextual popup panel when a row is selected.
     * Controls provide options to modify the schedule within the context of 
     * the selected row.
     */
    var showSchedulerControls = function(args){
        schedulerActions.currentItem = args.record;
        schedulerActions.cfg.setProperty("context",
            [args.el.id, "tl", "bl"]
        );
        schedulerActions.render();
        schedulerActions.show();
    }


    /**
     * @method setFilterMenuSelection
     * @description sets the value of a filter menu button
     */
     var setFilterMenuSelection = function(event){
         if(this.original_label == undefined){
             this.original_label = this.get("label");
         }
         var menuItem = event.newValue;
         var selectionLabel = (
            (menuItem && wrapText(menuItem.cfg.getProperty("text")))
            || this.original_label
        );
         this.set("label", selectionLabel);
     }

    /**
     * @method filterCalendarSetup
     * @description sets up a calendar bound to a button
     */
    var filterCalendarSetup = function(button, type, menu, callback){
        var sCalendar = new YAHOO.widget.Calendar(
            "calendar_start_" + type,
            menu.body.id
        );
        sCalendar.render();
        button.getSelectedDate = function(){
            var sDate = sCalendar.getSelectedDates()[0];
            var sDateText = "";
            if (sDate != null){
                sDateText = new Array(
                    sDate.getFullYear(), sDate.getMonth()+1, sDate.getDate()
                ).join("-")
            }
            return sDateText;
        };
        button.clearSelection = function(){
            sCalendar.deselectAll();
            button.set("label", button.original_label);
        }
        sCalendar.selectEvent.subscribe(function(sType, oArgs){
            if (button.original_label == undefined){
                button.original_label = button.get("label");
            }
            if(oArgs){
                var sDate = oArgs[0][0];
                button.set("label", wrapText(sDate.join("-")));
            }
            menu.hide();
        });
        button.unsubscribe("click", callback);
        sCalendar.align();
    }


    /*
     * @method getDummyCalendarDate
     * @description returns a blank string as selected calendar date associated
     * with a filter button.
     * 
     * This is used if the calendar has not been instantiated which is bound
     * to the click event of a fitler button.
     */
     var getDummyCalendarDate = function(){
         return "";
     }

   /**
     * @method renderAvailableItems
     * @description renders available items as tabs
     */
    var renderAvailableItems = function(args){
        if (available_items_loaded){ return; }
        available_items_loaded = true;
        var existing_record_keys = new Array();
        var record_set = itemsDataTable.getRecordSet().getRecords();
        for(index in record_set){
            data = record_set[index].getData();
            existing_record_keys.push(data.item_id + ":" + data.item_type);
        }

        /**
         * @method itemSelectorFormatter
         * @description renders checkboxes to select items on the schedule
         */
        var availableItemSelectFormatter = function(el, record, column, data){
            index = this.getTrIndex(record) + 1;
            record_key = (record.getData().item_id + ":" + record.getData().item_type).toString()
            checked = "";
            if(existing_record_keys.indexOf(record_key)>=0){
                checked = "checked='checked'";
            }
            el.innerHTML = "<input type='checkbox' name='rec-sel-" + index +"' " + checked + "/>"
        }

        var availableItemsColumns = [
            {
                key: ITEM_SELECT_ROW_COLUMN, 
                label: "<input type='checkbox' name='rec-sel-all'/>", 
                formatter: availableItemSelectFormatter
            },
            {
                key: "item_title",
                label: scheduler_globals.column_title,
            },
            {
                key: "registry_number",
                label: scheduler_globals.column_registry_number,
            },
            {
                key: ITEM_MOVER_COLUMN,
                label: scheduler_globals.column_mover,
            },
            {
                key: "status",
                label: scheduler_globals.column_status,
            },
            {
                key: "status_date",
                label: scheduler_globals.column_status_date,
                formatter: "date"
            },
        ]
        
        var availableItemsSchema = {
            resultsList: "items",
            fields: ["item_id", "item_type", "item_title", "status", "status_date", "registry_number", "mover"]
        }
        
        var availableItems = new YAHOO.widget.TabView();
        var itemsPanel = schedulerLayout.getUnitByPosition("center");
        for (type_index in scheduler_globals.schedulable_types){
            (function(){
                var typedef = scheduler_globals.schedulable_types[type_index];
                var type = typedef.name;
                var container_id = type + "-data-table";
                var container_id_filters = container_id + "-filters";
                availableItems.addTab(new YAHOO.widget.Tab(
                    {
                        label: typedef.title,
                        content: "<div id='" + container_id_filters + "' class='schedule-available-item-filters'></div>" + "<div id='" + container_id + "'/>",
                    }
                ));
                Event.onAvailable(container_id, function(event){
                    var tabDataSource = new YAHOO.util.DataSource(
                        scheduler_globals.schedulable_items_json_url + "?type="+ type
                    );
                    tabDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
                    tabDataSource.responseSchema = availableItemsSchema;
                    var tabDataTable = new YAHOO.widget.DataTable(container_id,
                        availableItemsColumns, tabDataSource, 
                        { 
                            selectionMode:"single",
                            scrollable: true,
                            initialLoad: true,
                            width: itemsPanel.body.clientWidth + "px",
                        }
                    );
                    tabDataTable.subscribe("cellClickEvent", addItemToSchedule);
                    tabDataTable.subscribe("theadCellClickEvent", checkRows);
                    tabDataTable.subscribe("cellSelectEvent", addItemToSchedule);
                    tabDataTable.subscribe("postRenderEvent", function(){
                        this.getHdTableEl().width = "100%";
                        this.getBdTableEl().width = "100%";
                    });
                    
                    //create filter controls
                    var filter_config = scheduler_globals.filter_config[type];
                    if (filter_config.menu.length > 0){
                        var statusFilterButton = new YAHOO.widget.Button(
                            {
                                type: "menu",
                                label: wrapText(filter_config.label),
                                id: "filter_status_" + type,
                                name: "filter_status_" + type,
                                menu: filter_config.menu,
                                container: container_id_filters,
                            }
                        );
                        statusFilterButton.on("selectedMenuItemChange",
                            setFilterMenuSelection
                        );

                        var dateStartMenu = new YAHOO.widget.Overlay(
                            "cal_menu_start_" + type, { visible: false }
                        );
                        var dateStartButton = new YAHOO.widget.Button(
                            {
                                type: "menu",
                                label: wrapText(
                                    scheduler_globals.filters_start_date_label
                                ),
                                id: "filter_start_date_" + type,
                                name: "filter_start_date_" + type,
                                menu: dateStartMenu,
                                container: container_id_filters,
                            }
                        );
                        dateStartButton.on("appendTo", function(){
                            dateStartMenu.setBody(" ");
                            dateStartMenu.body.id = "calendar_start_container_" + type;
                        });

                        dateStartButton.on("click", function callback(){
                            filterCalendarSetup(this, type, dateStartMenu, callback);
                        });

                        var dateEndMenu = new YAHOO.widget.Overlay(
                            "cal_menu_end_" + type, { visible: false }
                        );
                        var dateEndButton = new YAHOO.widget.Button(
                            {
                                type: "menu",
                                label: wrapText(
                                    scheduler_globals.filters_end_date_label
                                ),
                                id: "filter_end_date_" + type,
                                name: "filter_end_date_" + type,
                                menu: dateEndMenu,
                                container: container_id_filters,
                            }
                        );
                        dateEndButton.on("appendTo", function(){
                            dateEndMenu.setBody(" ");
                            dateEndMenu.body.id = "calendar_end_container_" + type;
                        });
                        
                        dateEndButton.on("click", function callback(){
                            filterCalendarSetup(this, type, dateEndMenu, callback);
                        });
                        
                        
                        dateStartButton.getSelectedDate = getDummyCalendarDate;
                        dateStartButton.clearSelection = getDummyCalendarDate;
                        dateEndButton.getSelectedDate = getDummyCalendarDate;
                        dateEndButton.clearSelection = getDummyCalendarDate;
                        
                        var filterApplyButton = new YAHOO.widget.Button(
                            {
                                type: "button",
                                label: wrapText(
                                    scheduler_globals.filter_apply_label
                                ),
                                id: "filter_apply_" + type,
                                name: "filter_apply_" + type,
                                container: container_id_filters,
                            }
                        );
                        filterApplyButton.on("click", function(oArgs){
                            var data_filters = {};
                            var selected_status = statusFilterButton.getMenu().activeItem;
                            if (selected_status != null){
                                data_filters["filter_status"] = selected_status.value;
                            }
                            var start_date = dateStartButton.getSelectedDate();
                            var end_date = dateEndButton.getSelectedDate();
                            if (start_date || end_date){
                                data_filters["filter_status_date"] = new Array(
                                        (start_date || ""), (end_date|| "")
                                ).join("|");
                            }
                            if (Object.keys(data_filters).length > 0){
                                tabDataTable.refresh(data_filters);
                            }else{
                                saveDialog.setHeader(scheduler_globals.filters_no_filters_header);
                                saveDialog.setBody(scheduler_globals.filters_no_filters_message);
                                saveDialog.show();
                                saveDialog.bringToTop();
                            }
                        });
                        
                        var clearFiltersButton = new YAHOO.widget.Button(
                            {
                                type: "button",
                                label: wrapText(
                                    scheduler_globals.filters_clear_label
                                ),
                                id: "filter_clear_" + type,
                                name: "filter_clear_" + type,
                                container: container_id_filters,
                            }
                        );
                        clearFiltersButton.on("click", function(oArgs){
                            //reset filters and then reload datatable
                            statusFilterButton.set("selectedMenuItem", null);
                            dateStartButton.clearSelection();
                            dateEndButton.clearSelection();
                            tabDataTable.refresh();
                        });

                    }
                    schedulerLayout.on("resize", function(){
                        itemsDataTable.setAttributes({
                            "width": this.getUnitByPosition("left").body.clientWidth + "px"
                        }, true);
                        tabDataTable.setAttributes({
                            "width": this.getUnitByPosition("center").body.clientWidth + "px"
                        }, true);
                    });
                });
            })();
        }
        availableItems.selectTab(0);
        availableItems.appendTo(itemsPanel.body);
    }


    /**
     * @method renderSchedule
     * @description renders the schedule to the provided container element
     **/
     var renderSchedule = function(container){
        var columnDefinitions = [
            {
                key:"item_type", 
                label: scheduler_globals.column_type,
                formatter: itemTypeFormatter,
            },
            {
                key:"item_title", 
                label: scheduler_globals.column_title,
                editor: new YAHOO.widget.TextboxCellEditor(),
                formatter: itemTitleFormatter
            },
            {
                key:ITEM_MOVE_UP_COLUMN, 
                label:"", 
                formatter:itemMoveUpFormatter 
            },
            {
                key:ITEM_MOVE_DOWN_COLUMN, 
                label:"", 
                formatter:itemMoveDownFormatter
            },
        ];
        
        itemsDataSource = new YAHOO.util.DataSource(
            scheduler_globals.json_listing_url
        );
        itemsDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        itemsDataSource.responseSchema = {
            resultsList: "nodes",
            fields: ["item_id", "item_title", "item_type", "object_id", ITEM_MOVER_COLUMN],
            metaFields: { localPermissions: "localPermissions" },
        };
        
        var scheduler_container = document.createElement("div");
        container.appendChild(scheduler_container);

        itemsDataTable = new YAHOO.widget.DataTable(scheduler_container,
            columnDefinitions, itemsDataSource, 
            { 
                selectionMode:"single",
                scrollable:true,
                width:container.clientWidth + "px",
            }
        );
        itemsDataTable.subscribe("rowMouseoverEvent", itemsDataTable.onEventHighlightRow);
        itemsDataTable.subscribe("rowMouseoutEvent", itemsDataTable.onEventUnhighlightRow);
        itemsDataTable.subscribe("rowClickEvent", itemsDataTable.onEventSelectRow);
        itemsDataTable.subscribe("cellDblclickEvent", showCellEditorHandler);
        itemsDataTable.subscribe("cellClickEvent", reorderRow);
        itemsDataTable.subscribe("rowSelectEvent", showSchedulerControls);
        itemsDataTable.subscribe("initEvent", renderAvailableItems);
        itemsDataTable.subscribe("initEvent", highlightTypedRows);
        itemsDataTable.subscribe("initEvent", initShowSchedulerControls);
        itemsDataTable.subscribe("rowDeleteEvent", initShowSchedulerControls);
        itemsDataTable.subscribe("rowAddEvent", highlightTypedRows);
        itemsDataTable.subscribe("rowAddEvent", hideSchedulerControls);
        itemsDataTable.subscribe("postRenderEvent", function(){
            this.getHdTableEl().width = "100%";
            this.getBdTableEl().width = "100%";
        });
        itemsDataTable.doBeforeLoadData = function(oRequest, oResponse, oPayload){
            localPermissions = oResponse.meta.localPermissions;
            return oPayload;
        }
        
        return {
            oDS: itemsDataSource,
            oDT: itemsDataTable,
        }
     }

    /**
     * @method removeCheckedItems
     * @description removes checked items from the schedule
     **/
    var removeCheckedItems = function(args){
        var record_set = itemsDataTable.getRecordSet().getRecords();
        var checked_ids = new Array()
        for (record_index in record_set){
            var row = itemsDataTable.getTrEl(record_set[record_index]);
            var select_td = itemsDataTable.getFirstTdEl(row);
            if(Y$.query(CHECK_BOX_SELECTOR, select_td, true).checked){
                checked_ids.push(record_index);
            }
        }
        checked_ids.reverse();
        for (idx in checked_ids){
            itemsDataTable.deleteRow(Number(checked_ids[idx]));
        }
    }
    
    /**
     * @method discardChanges
     * @description reloads the scheduling page losing all local changes
     **/
    var discardChanges = function(args){
        window.location.reload();
    }

    //schedule save callback config
    var RequestObject = {
        handleSuccess: function(o){
            savingDialog.setBody(scheduler_globals.saving_dialog_refreshing);
            itemsDataTable.refresh();
            savingDialog.setBody("");
            savingDialog.hide();
        },
        handleFailure: function(o){
            savingDialog.setBody(scheduler_globals.saving_dialog_exception);
            setTimeout(function(){
                    savingDialog.setBody("");
                    savingDialog.hide("");
                },
                2000
            );
        },
        startRequest: function(data){
            savingDialog.setBody(scheduler_globals.saving_dialog_text);
            savingDialog.show();
            savingDialog.bringToTop();
            YCM.asyncRequest("POST", 
                scheduler_globals.save_schedule_url,
                callback,
                data
            );
                
        }
    }
    
    var callback = {
        success: RequestObject.handleSuccess,
        failure: RequestObject.handleFailure,
        scope: RequestObject
    }

    /**
     * @method saveSchedule
     * @description posts schedule data to bungeni for persistence
     **/
    var saveSchedule = function(args){
        var record_set = itemsDataTable.getRecordSet();
        var records = record_set.getRecords();
        if (record_set.getLength()){
            var item_data = new Array();
            for (index in records){
                var record_data = records[index].getData();
                var save_data = {
                    item_type: record_data.item_type,
                    item_id: record_data.item_id,
                    schedule_id: record_data.object_id,
                    item_text: record_data.item_title
                }
                item_data.push(YJSON.stringify(save_data));
            }
            var post_data = "data=" + YJSON.stringify(item_data);
            RequestObject.startRequest(post_data);
        }else{
            saveDialog.show();
            saveDialog.bringToTop();
        }
    }

    /**
     * @method renderScheduleButtons
     * @description Renders action buttons inside provided container element
     **/
    var renderScheduleButtons = function(container){
        container.style.lineHeight = container.clientHeight;
        container.style.padding = "5px";
        var saveButton = new YAHOO.widget.Button(
            { label: scheduler_globals.save_button_text }
        );
        var discardButton = new YAHOO.widget.Button(
            { label: scheduler_globals.discard_button_text }
        );
        saveButton.on("click", saveSchedule);
        discardButton.on("click", discardChanges);
        saveButton.appendTo(container);
        discardButton.appendTo(container);
    }

    /**
     * @method addItemToSchedule
     * @description adds available item to schedule
     * 
     */
    var addItemToSchedule = function(args){
        var target = args.target || args.el;
        var target_column = this.getColumn(target);
        if(target_column.field == ITEM_SELECT_ROW_COLUMN){
            var targetRecord = this.getRecord(target);
            var targetData = targetRecord.getData()
            if (Y$.query(CHECK_BOX_SELECTOR, target, true).checked){
                //check if item is already scheduled
                var record_set = itemsDataTable.getRecordSet().getRecords();
                var item_in_schedule = false;
                for(idx in record_set){
                    var record = record_set[idx];
                    var oData = record.getData();
                    if((oData.item_id == targetData.item_id) &&
                        (oData.item_type == targetData.item_type)
                    ){
                        item_in_schedule = true;
                        break;
                    }
                }
                if (!item_in_schedule){
                    var new_record_data = {
                        item_id: targetData.item_id,
                        item_title: targetData.item_title,
                        item_type: targetData.item_type,
                        item_mover: targetData.item_mover,
                    }
                    ctx_index = itemsDataTable.getSelectedRows()[0];
                    var new_record_index = (
                        (ctx_index && itemsDataTable.getTrIndex(ctx_index)+1) || 0
                    );
                    itemsDataTable.addRow(new_record_data, new_record_index);
                }
            }else{
                var record_set = itemsDataTable.getRecordSet().getRecords();
                for (idx in record_set){
                    var record = record_set[idx];
                    var sdata = record.getData();
                    if((sdata.item_id == targetData.item_id) &&
                        (sdata.item_type == targetData.item_type)
                    ){
                        itemsDataTable.deleteRow(Number(idx));
                    }
                }
            }
        }
    }

    /**
     * @method checkRows
     * @description check or uncheck selectors for all items on data table
     * 
     */
    var checkRows = function(args){
        var target_column = this.getColumn(args.target);
        if(target_column.field == ITEM_SELECT_ROW_COLUMN){
            var record_set = this.getRecordSet().getRecords();
            var checked = false;
            if (Y$.query(CHECK_BOX_SELECTOR, args.target, true).checked){
                checked = true;
            }
            for (record_index in record_set){
                var row = this.getTrEl(record_set[record_index]);
                var select_td = this.getFirstTdEl(row);
                Y$.query(CHECK_BOX_SELECTOR, select_td, true).checked = checked;
                this.unselectAllCells();
                this.selectCell(select_td);
            }
        }
    }


    /**
     * @method anonymous
     * @description Renders the panel UI and builds up schedule data table.
     * Also binds various events to handlers on the data table.
     * Schedule control actions are also built into the DOM
     **/
    Event.onDOMReady(function(){
        //create scheduler actions panel
        schedulerActions = new YAHOO.widget.Panel("scheduled-item-controls",
            {   
                underlay: "none",
                width: "300px",
            }
        );
        schedulerActions.currentItem = null;
        
        var scheduleTextButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.text_button_text,
            }
        );
        var scheduleHeadingButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.heading_button_text,
            }
        );
        var scheduleRemoveButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.remove_button_text,
            }
        );
        scheduleTextButton.appendTo(schedulerActions.body);
        scheduleTextButton.on("click", addTextToSchedule);
        scheduleHeadingButton.appendTo(schedulerActions.body);
        scheduleHeadingButton.on("click", addHeadingToSchedule);
        scheduleRemoveButton.appendTo(schedulerActions.body);
        scheduleRemoveButton.on("click", removeSelectedRow);

        //create delete dialog and controls
        deleteDialog = new YAHOO.widget.SimpleDialog("scheduler-delete-dialog",
            DIALOG_CONFIG
        );
        deleteDialog.setHeader(scheduler_globals.delete_dialog_header);
        deleteDialog.setBody(scheduler_globals.delete_dialog_text)
        
        var handleDeleteConfirm = function(){
            selected_record_index = itemsDataTable.getSelectedRows()[0];
            itemsDataTable.deleteRow(selected_record_index);
            this.hide();
            schedulerActions.hide();
        }
        
        var handleDeleteCancel = function(){
            this.hide();
        }
        
        var deleteDialogButtons = [
            {
                text: scheduler_globals.delete_dialog_confirm, 
                handler: handleDeleteConfirm
            },
            {
                text: scheduler_globals.delete_dialog_cancel, 
                handler: handleDeleteCancel,
                isDefault: true
            },
        ] 
        
        deleteDialog.cfg.queueProperty("buttons", deleteDialogButtons);
        deleteDialog.cfg.queueProperty("icon", 
            YAHOO.widget.SimpleDialog.ICON_WARN
        );
        deleteDialog.render(document.body);

        //create save dialog
        saveDialog = new YAHOO.widget.SimpleDialog("scheduler-save-dialog",
            DIALOG_CONFIG
        );
        saveDialog.setHeader(scheduler_globals.save_dialog_header);
        saveDialog.setBody(scheduler_globals.save_dialog_empty_message)
                
        var handleConfirm = function(){
            this.hide();
        }
        
        var saveDialogButtons = [
            {
                text: scheduler_globals.save_dialog_confirm, 
                handler: handleConfirm
            }
        ] 
        
        saveDialog.cfg.queueProperty("buttons", saveDialogButtons);
        saveDialog.cfg.queueProperty("icon",
            YAHOO.widget.SimpleDialog.ICON_INFO
        );
        saveDialog.render(document.body);
        
        //render schedule processing dialog
        savingDialog = new YAHOO.widget.SimpleDialog("scheduler-saving-dialog",
            DIALOG_CONFIG
        );
        savingDialog.setHeader(scheduler_globals.saving_dialog_header);
        savingDialog.setBody("");
        savingDialog.cfg.queueProperty("close", false);
        savingDialog.cfg.queueProperty("icon",
            YAHOO.widget.SimpleDialog.ICON_BLOCK
        );
        savingDialog.render(document.body);
        
        //create layout
        schedulerLayout = new YAHOO.widget.Layout("scheduler-layout",
            {
                height:500,
                units: [
                    { 
                        position: "left", 
                        width: 600, 
                        body: '',
                        gutter: "5 5",
                        height: 400,
                        resize: true,
                        collapse: true
                    },
                    { 
                        position: "center", 
                        body: '',
                        header: scheduler_globals.available_items_title,
                        gutter: "5 5",
                        height: 400,
                    },
                ]
            }
        );
        
        var schedulerInnerLayout = null;
        
        //render inner scheduler layout
        schedulerLayout.on("render", function(){
            var left_el = schedulerLayout.getUnitByPosition("left").get("wrap");
            innerLayout = new YAHOO.widget.Layout(left_el,
                {
                    parent: schedulerLayout,
                    units: [
                        {
                            position:"center", 
                            header: scheduler_globals.current_schedule_title,
                            body: "" 
                        },
                        {
                            position:"bottom", 
                            height: 40, 
                            body:""
                        },
                    ]
                }
            );
            innerLayout.on("render", function(){
                renderSchedule(this.getUnitByPosition("center").body);
                renderScheduleButtons(this.getUnitByPosition("bottom").body);
            });
            innerLayout.render();
        });
        
        //render available items tabs
        schedulerLayout.render();
    });
})();
