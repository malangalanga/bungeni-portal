/*
 * This module instatiates a datatable for items in sitting. We also render
 * a panel with items available for scheduling - this is a pre-populated 
 * viewlet
 * 
 */
YAHOO.util.Event.addListener(window, "load", function(){
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
            columnDefinitions, itemsDataSource
        );
        
        return {
            oDS: itemsDataSource,
            oDT: itemsDataTable
        };
    }();
    
    //create panel
    var build_items_panel = function(){
        var itemsPanel = new YAHOO.widget.Panel("unscheduled-items-panel");
        itemsPanel.render();
        itemsPanel.show();
        itemsPanel.center();
    }();
});
