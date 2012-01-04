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
    var deleteDialog = null;
    var saveDialog = null;
    var savingDialog = null;
    var ITEM_SELECT_ROW_COLUMN = "item_select_row"
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

    /**
     * Custom method of added to data table to refresh data
     **/
    YAHOO.widget.DataTable.prototype.refresh = function() {
        var datasource = this.getDataSource();
        datasource.sendRequest(
                (this.get("initialRequest")),
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
    var addTextToSchedule = function(event){
        var currentItem = schedulerActions.currentItem;
        var new_record_index = itemsDataTable.getTrIndex(currentItem) + 1;
        itemsDataTable.addRow(
            { 
                item_title: scheduler_globals.initial_editor_text, 
                item_type: "text"
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
     * @method deleteRow
     * @description deletes a row and record from the schedule. Displays
     * a dialog to confirm intention before deleting item
     * */
    var deleteRow = function(args){
        var target_column = this.getColumn(args.target);
        if (target_column.field == ITEM_DELETE_COLUMN){
            var target_record = this.getRecord(args.target);
            var target_index = this.getTrIndex(target_record);
            this.unselectAllRows();
            this.selectRow(target_index);
            deleteDialog.show();
            deleteDialog.bringToTop();
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
            }
        }
    }

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
     * @method showSchedulerControls
     * @description displays a contextual popup panel when a row is selected.
     * Controls provide options to modify the schedule within the context of 
     * the selected row.
     */
    var showSchedulerControls = function(args){
        schedulerActions.currentItem = args.record;
        schedulerActions.cfg.setProperty("context",
            [args.el.id, "tl", "tr"]
        );
        schedulerActions.render();
        schedulerActions.show();
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
                key: "item_type",
                label: scheduler_globals.column_type,
            },
            {
                key: "registry_number",
                label: scheduler_globals.column_registry_number,
            },
            {
                key: "mover",
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
        for (type_index in scheduler_globals.schedulable_types){
            (function(){
                var type = scheduler_globals.schedulable_types[type_index];
                var container_id = type + "data-table";
                availableItems.addTab(new YAHOO.widget.Tab(
                    {
                        label: type,
                        content: "<div id='" + container_id + "'/>",
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
                        }
                    );
                    tabDataTable.subscribe("cellClickEvent", addItemToSchedule);
                    tabDataTable.subscribe("theadCellClickEvent", checkRows);
                });
            })();
        }
        var itemsPanel = schedulerLayout.getUnitByPosition("center");
        availableItems.selectTab(0);
        availableItems.appendTo(itemsPanel.body);
    }


    /**
     * @method renderSchedule
     * @description renders the schedule to the provided container element
     **/
     var renderSchedule = function(container){
        var textCellEditor = YAHOO.widget.TextboxCellEditor;
        var columnDefinitions = [
            {
                key:ITEM_SELECT_ROW_COLUMN, 
                label: "<input type='checkbox' name='rec-sel-all'/>", 
                formatter: itemSelectFormatter 
            },
            {
                key:"item_title", 
                label: scheduler_globals.column_title,
                editor: new YAHOO.widget.TextboxCellEditor(),
            },
            {key:"item_type", label: scheduler_globals.column_type},
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
            {
                key:ITEM_DELETE_COLUMN,
                label:"",
                formatter:itemDeleteFormatter
            }
        ];
        
        itemsDataSource = new YAHOO.util.DataSource(
            scheduler_globals.json_listing_url
        );
        itemsDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        itemsDataSource.responseSchema = {
            resultsList: "nodes",
            fields: ["item_id", "item_title", "item_type", "object_id"],
        };
        
        var scheduler_container = document.createElement("div");
        container.appendChild(scheduler_container);

        itemsDataTable = new YAHOO.widget.DataTable(scheduler_container,
            columnDefinitions, itemsDataSource, 
            { 
                selectionMode:"single",
                scrollable: true,
                width:"100%",
            }
        );
        itemsDataTable.subscribe("rowMouseoverEvent", itemsDataTable.onEventHighlightRow);
        itemsDataTable.subscribe("rowMouseoutEvent", itemsDataTable.onEventUnhighlightRow);
        itemsDataTable.subscribe("rowClickEvent", itemsDataTable.onEventSelectRow);
        itemsDataTable.subscribe("cellDblclickEvent", showCellEditorHandler);
        itemsDataTable.subscribe("cellClickEvent", reorderRow);
        itemsDataTable.subscribe("rowSelectEvent", showSchedulerControls);
        itemsDataTable.subscribe("cellClickEvent", deleteRow);
        itemsDataTable.subscribe("theadCellClickEvent", checkRows);
        itemsDataTable.subscribe("initEvent", renderAvailableItems);
        itemsDataTable.subscribe("initEvent", highlightTypedRows);
        itemsDataTable.subscribe("rowAddEvent", highlightTypedRows);
        
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
        var removeButton = new YAHOO.widget.Button(
            { label: scheduler_globals.remove_button_text }
        );
        var saveButton = new YAHOO.widget.Button(
            { label: scheduler_globals.save_button_text }
        );
        var discardButton = new YAHOO.widget.Button(
            { label: scheduler_globals.discard_button_text }
        );
        removeButton.on("click", removeCheckedItems);
        saveButton.on("click", saveSchedule);
        discardButton.on("click", discardChanges);
        removeButton.appendTo(container);
        saveButton.appendTo(container);
        discardButton.appendTo(container);
    }

    /**
     * @method addItemToSchedule
     * @description adds available item to schedule
     * 
     */
    var addItemToSchedule = function(args){
        var target_column = this.getColumn(args.target);
        if(target_column.field == ITEM_SELECT_ROW_COLUMN){
            var targetRecord = this.getRecord(args.target);
            var targetData = targetRecord.getData()
            if (Y$.query(CHECK_BOX_SELECTOR, args.target, true).checked){
                var new_record_data = {
                    item_id: targetData.item_id,
                    item_title: targetData.item_title,
                    item_type: targetData.item_type,
                }
                itemsDataTable.addRow(new_record_data);
            }else{
                var record_set = itemsDataTable.getRecordSet().getRecords();
                for (idx in record_set){
                    var record = record_set[idx];
                    var sdata = record.getData();
                    if((sdata.item_id == targetData.item_id) &&
                        (sdata.item_type == sdata.item_type)
                    ){
                        itemsDataTable.deleteRow(Number(idx));
                    }
                }
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
                underlay: "none"
            }
        );
        schedulerActions.currentItem = null;
        
        var scheduleTextButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.text_button_text,
            }
        );
        scheduleTextButton.appendTo(schedulerActions.body);
        scheduleTextButton.on("click", addTextToSchedule);
        
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
                        height: 400 
                    },
                    { 
                        position: "center", 
                        body: '',
                        header: scheduler_globals.available_items_title,
                        gutter: "5 5",
                        height: 400 
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
