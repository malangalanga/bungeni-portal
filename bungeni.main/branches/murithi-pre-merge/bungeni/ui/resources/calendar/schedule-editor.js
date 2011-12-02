/*
 * This module instatiates a datatable for items in sitting. We also render
 * a panel with items available for scheduling - this is a pre-populated 
 * viewlet
 * 
 */
YAHOO.util.Event.addListener(window, "load", function(){
    var scheduledActions = new YAHOO.widget.Panel("scheduled-item-controls",
        {   
            underlay: "none"
        }
    );
    scheduledActions.currentItem = null;
    
    var commentButton = new YAHOO.util.Element("add-note");
    commentButton.on("click", function(event){
        console.log("Processing record", scheduledActions.currentItem);
    });
    
    var datatable_loader = function(){
        
        var columnDefinitions = [
            {key: "item_id", label: scheduler_globals.column_title},
            {key: "item_type", label: scheduler_globals.column_type},
        ];
        
        var itemsDataSource = new YAHOO.util.DataSource(
            scheduler_globals.json_listing_url
        );
        itemsDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        itemsDataSource.responseSchema = {
            resultsList: "nodes",
            fields: ["item_id", "item_type"],
        };
        
        var itemsDataTable = new YAHOO.widget.DataTable("schedule-table",
            columnDefinitions, itemsDataSource, { selectionMode:"single" }
        );

        itemsDataTable.subscribe("rowMouseoverEvent", itemsDataTable.onEventHighlightRow);
        itemsDataTable.subscribe("rowMouseoutEvent", itemsDataTable.onEventUnhighlightRow);
        itemsDataTable.subscribe("rowClickEvent", itemsDataTable.onEventSelectRow);

        itemsDataTable.subscribe("rowHighlightEvent", function(args){
            scheduledActions.currentItem = args.record;
            console.log(args.record);
            scheduledActions.cfg.setProperty("context",
                [args.el.id, "tl", "tr"]
            );
            scheduledActions.render();
            scheduledActions.show();
        });
        
        return {
            oDS: itemsDataSource,
            oDT: itemsDataTable
        };
    }();
    
});
