/*
 * This module instatiates a datatable for items in sitting. We also render
 * a panel with items available for scheduling.
 * 
 */

(function() {
    var Dom = YAHOO.util.Dom, Event = YAHOO.util.Event, Y$ = YAHOO.util.Selector;
    var itemsDataTable = null;
    var itemsDataSource = null;
    var schedulerActions = null;
    var deleteDialog = null;
    var ITEM_SELECT_ROW_COLUMN = "item_select_row"
    var ITEM_MOVE_UP_COLUMN = "item_move_up";
    var ITEM_MOVE_DOWN_COLUMN = "item_move_down";
    var ITEM_DELETE_COLUMN = "item_delete";
    var CHECK_BOX_SELECTOR = "input[type=checkbox]"

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
                item_id: scheduler_globals.initial_editor_text, 
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
        schedulerActions.close();
    }
    
    /**
     * @method showCellEditor
     * @description displays an editor to modify text records on the schedule
     */
    var showCellEditor = function(event){
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
                var data_one = this.getRecord(swap_rows[0]).getData();
                var data_two = this.getRecord(swap_rows[1]).getData();
                this.updateRow(swap_rows[0], data_two)
                this.updateRow(swap_rows[1], data_one)
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
                key:"item_id", 
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
            fields: ["item_id", "item_type"],
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
        itemsDataTable.subscribe("cellDblclickEvent", showCellEditor);
        itemsDataTable.subscribe("cellClickEvent", reorderRow);
        itemsDataTable.subscribe("rowSelectEvent", showSchedulerControls);
        itemsDataTable.subscribe("cellClickEvent", deleteRow);
        itemsDataTable.subscribe("theadCellClickEvent", checkRows);
        
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
                    object_id: targetData.item_id,
                    item_id: targetData.item_title,
                    item_type: targetData.item_type,
                }
                itemsDataTable.addRow(new_record_data);
            }else{
                var record_set = itemsDataTable.getRecordSet().getRecords();
                for (idx in record_set){
                    var record = record_set[idx];
                    if(record.getData().object_id == targetData.item_id){
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
            {
                width: "auto",
                fixedcenter: true,
                modal: true,
                visible: false,
                draggable: false,
            }
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
        deleteDialog.render(document.body);
        
        //create layout
        var schedulerLayout = new YAHOO.widget.Layout("scheduler-layout",
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
        
        
        //load data table
        schedulerLayout.on("render", function(){
            var textCellEditor = YAHOO.widget.TextboxCellEditor;
            var columnDefinitions = [
                {
                    key:ITEM_SELECT_ROW_COLUMN, 
                    label: "<input type='checkbox' name='rec-sel-all'/>", 
                    formatter: itemSelectFormatter 
                },
                {
                    key:"item_id", 
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
                fields: ["item_id", "item_type"],
            };
            
            var layout_centre = schedulerLayout.getUnitByPosition("left");
            var scheduler_container = document.createElement("div");
            layout_centre.body.appendChild(scheduler_container);

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
            itemsDataTable.subscribe("cellDblclickEvent", showCellEditor);
            itemsDataTable.subscribe("cellClickEvent", reorderRow);
            itemsDataTable.subscribe("rowSelectEvent", showSchedulerControls);
            itemsDataTable.subscribe("cellClickEvent", deleteRow);
            itemsDataTable.subscribe("theadCellClickEvent", checkRows);
            
            return {
                oDS: itemsDataSource,
                oDT: itemsDataTable,
            }
        });
        
        //render available items tabs
        schedulerLayout.on("render", function(){
            var availableItemsColumns = [
                {
                    key: ITEM_SELECT_ROW_COLUMN, 
                    label: "<input type='checkbox' name='rec-sel-all'/>", 
                    formatter: itemSelectFormatter 
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
                    key: "status",
                    label: scheduler_globals.column_status,
                },
            ]
            
            var availableItemsSchema = {
                resultsList: "items",
                fields: ["item_id", "item_type", "item_title", "status"]
            }
            
            var availableItems = new YAHOO.widget.TabView();
            for (type_index in scheduler_globals.schedulable_types){
                (function(){
                    var type = scheduler_globals.schedulable_types[type_index];
                    var container_id = type + "data-table";
                    availableItems.addTab(new YAHOO.widget.Tab(
                        {
                            label: type,
                            content: "<div id='" + container_id +"'>Intel Inside</div>",
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
        });
        schedulerLayout.render();
    });
})();
