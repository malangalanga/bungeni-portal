/*
 * This module instatiates a datatable for items in sitting. We also render
 * a panel with items available for scheduling - this is a pre-populated 
 * viewlet
 * 
 */

(function() {
    var Dom = YAHOO.util.Dom, Event = YAHOO.util.Event, itemsDataTable = null;
    var onTextRecordAdded = new YAHOO.util.CustomEvent("onTextRecordAdded");
    
    Event.onDOMReady(function(){
        //create datatable controls
        var scheduledActions = new YAHOO.widget.Panel("scheduled-item-controls",
            {   
                underlay: "none"
            }
        );
        scheduledActions.currentItem = null;
        
        var scheduleTextButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.text_button_text,
            }
        );
        scheduleTextButton.appendTo(scheduledActions.footer);
        scheduleTextButton.on("click", function(event){
            var new_record_index = itemsDataTable.getTrIndex(
                scheduledActions.currentItem
            ) + 1;
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
            itemsDataTable.unselectAllRows();
            itemsDataTable.selectRow(new_record);
            /*var firstCell = itemsDataTable.getFirstTdEl(
                itemsDataTable.getSelectedTrEls()[0]
            );
            var editCell = itemsDataTable.getNextTdEl(firstCell);
            //TODO - fire showCellEditor*/
            scheduledActions.close();
        });
        var removeButton = new YAHOO.widget.Button(
            {
                label: scheduler_globals.remove_button_text
            }
        );
        removeButton.appendTo(scheduledActions.footer);
        
        //var itemNumberFormatter = function(el, record, column, data){
        //    el.innerHTML = itemsDataTable.getTrIndex(record) + 1;
        //}
        
        var itemSelectFormatter = function(el, record, column, data){
            index = itemsDataTable.getTrIndex(record) + 1;
            el.innerHTML = "<input type='checkbox' name='rec-sel-" + index + "'/>"
        }
        
        //create layout
        schedulerLayout = new YAHOO.widget.Layout("scheduler-layout",
            {
                height:500,
                units: [
                    { 
                        position: "left", 
                        width: 600, 
                        body: '',
                        header: scheduler_globals.current_schedule_title,
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
        
        //load data table
        schedulerLayout.on("render", function(){
            var textCellEditor = YAHOO.widget.TextboxCellEditor;
            var columnDefinitions = [
                {
                    key:"item_checked", 
                    label: "<input type='checkbox' name='rec-sel-all'/>", 
                    formatter: itemSelectFormatter 
                },
                {
                    key:"item_id", 
                    label: scheduler_globals.column_title,
                    editor: new YAHOO.widget.TextboxCellEditor(),
                },
                {key:"item_type", label: scheduler_globals.column_type},
            ];
            
            var itemsDataSource = new YAHOO.util.DataSource(
                scheduler_globals.json_listing_url
            );
            itemsDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
            itemsDataSource.responseSchema = {
                resultsList: "nodes",
                fields: ["item_id", "item_type"],
            };
            
            layout_centre = schedulerLayout.getUnitByPosition("left");
            var scheduler_container = document.createElement("div");
            layout_centre.body.appendChild(scheduler_container);

            itemsDataTable = new YAHOO.widget.DataTable(scheduler_container,
                columnDefinitions, itemsDataSource, { selectionMode:"single" }
            );
            itemsDataTable.subscribe("rowMouseoverEvent", itemsDataTable.onEventHighlightRow);
            itemsDataTable.subscribe("rowMouseoutEvent", itemsDataTable.onEventUnhighlightRow);
            itemsDataTable.subscribe("rowClickEvent", itemsDataTable.onEventSelectRow);
            //itemsDataTable.subscribe("onTextRecordAdded", itemsDataTable.onEventShowCellEditor);
            itemsDataTable.subscribe("cellDblclickEvent", function(event){
                var target = Event.getTarget(event);
                var record = this.getRecord(target);
                if (record.getData().item_type == "text"){
                    itemsDataTable.onEventShowCellEditor(event);
                }
            });

            itemsDataTable.subscribe("rowSelectEvent", function(args){
                scheduledActions.currentItem = args.record;
                scheduledActions.cfg.setProperty("context",
                    [args.el.id, "tl", "tr"]
                );
                scheduledActions.render();
                scheduledActions.show();
            });
            return {
                oDS: itemsDataSource,
                oDT: itemsDataTable,
            }
        });
        
        schedulerLayout.render();
    });
})();
