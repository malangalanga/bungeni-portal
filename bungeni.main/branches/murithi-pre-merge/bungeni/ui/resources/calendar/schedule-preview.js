/**
 * Render a preview of the Agenda
*/
YAHOO.bungeni.schedulingpreview = function(){
    var Event = YAHOO.util.Event;
    var cols = YAHOO.bungeni.config.scheduling.columns;
    var formatters = YAHOO.bungeni.config.scheduling.formatters;
    Event.onDOMReady(function(){
        var columns = [
            {
                key : cols.TYPE_COLUMN, 
                label : scheduler_globals.column_type,
            },
            {
                key : cols.TITLE_COLUMN, 
                label : scheduler_globals.column_title,
            },
            {
                key : cols.URI_COLUMN, 
                label : "",
                formatter: formatters.viewLink
            },
        ];
        var dataSource = new YAHOO.util.DataSource(
            scheduler_globals.json_listing_url
        );
        dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        dataSource.responseSchema = {
            resultsList: "nodes",
            fields: [
                cols.ID_COLUMN, 
                cols.TITLE_COLUMN, 
                cols.TYPE_COLUMN, 
                cols.OBJECT_ID_COLUMN, 
                cols.MOVER_COLUMN, 
                cols.URI_COLUMN
            ],
        };
        var dataTable = new YAHOO.widget.DataTable("schedule-table",
            columns, dataSource,
            {
                selectionMode:"single",
                scrollable:true,
                width:"100%"
            }
        );
    });
}();
