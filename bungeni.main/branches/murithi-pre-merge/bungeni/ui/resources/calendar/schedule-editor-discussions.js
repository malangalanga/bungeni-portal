/**
 * This module renders UI components that hadle editing of minutes.
**/
YAHOO.namespace("bungeni");
var ID_COLUMN = "item_id";
var OBJECT_ID_COLUMN = "object_id";
var TYPE_COLUMN = "item_type";
var TITLE_COLUMN = "item_title";
var MOVE_UP_COLUMN = "item_move_up";
var MOVE_DOWN_COLUMN = "item_move_down";
var MOVER_COLUMN = "item_mover";
var URI_COLUMN = "item_uri";

YAHOO.bungeni.formatters = function(){
    /**
     * @method itemTypeFormatter
     * @description render item type in reduced form
     */
     var itemTypeFormatter = function(el, record, column, data){
         el.innerHTML = ("<span style='font-size:10px;'>" + 
            record.getData()[TYPE_COLUMN] + "</span>"
        );
     }


    /**
     * @method itemTitleFormatter
     * @description renders title, emphasized text for titles and italicized
     * text for text records
     */
     var itemTitleFormatter = function(el, record, column, data){
         rec_data = record.getData();
         if(rec_data.item_type == scheduler_globals.types.HEADING){
             el.innerHTML = (
                "<span style='text-align:center;display:block;'><strong>" + 
                rec_data.item_title + "</strong></span>"
            );
         }else if(rec_data.item_type == scheduler_globals.types.TEXT){
             el.innerHTML = wrapText(rec_data.item_title);
         }else{
             if (rec_data.item_uri){
                el.innerHTML = (rec_data.item_title + 
                    "<em style='display:block;'><span>" +
                    scheduler_globals.text_moved_by + " : " + 
                    rec_data.item_mover + "</span>&nbsp;&nbsp;" +
                    "<a href=''" + rec_data.item_uri + ">" +
                    scheduler_globals.text_action_view + "</a></em>"
                );
            }else{
                el.innerHTML = (rec_data.item_title + 
                    "<em><span style='display:block;'>Moved by: " 
                    + rec_data.item_mover + "</span></em>"
                );
            }
         }
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

     
     return {
         titleFormatter: itemTitleFormatter,
         typeFormatter: itemTypeFormatter,
         moveUpFormatter: itemMoveUpFormatter,
         moveDownFormatter: itemMoveDownFormatter
     }
}();

YAHOO.bungeni.scheduling = function(){
    Event = YAHOO.util.Event;
    
    Event.onDOMReady(function(){
        YAHOO.bungeni.schedule = function(){
            var columns = [
                {
                    key:TYPE_COLUMN, 
                    label: scheduler_globals.column_type,
                    formatter: YAHOO.bungeni.formatters.typeFormatter,
                },
                {
                    key:TITLE_COLUMN, 
                    label: scheduler_globals.column_title,
                    editor: new YAHOO.widget.TextareaCellEditor(),
                    formatter: YAHOO.bungeni.formatters.titleFormatter
                },
                {
                    key:MOVE_UP_COLUMN, 
                    label:"", 
                    formatter:YAHOO.bungeni.formatters.moveUpFormatter
                },
                {
                    key:MOVE_DOWN_COLUMN, 
                    label:"", 
                    formatter:YAHOO.bungeni.formatters.moveDownFormatter
                },
            ];
            var dataSource = new YAHOO.util.DataSource(
                scheduler_globals.json_listing_url
            );
            dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
            dataSource.responseSchema = {
                resultsList: "nodes",
                fields: [
                    ID_COLUMN, 
                    TITLE_COLUMN, 
                    TYPE_COLUMN, 
                    OBJECT_ID_COLUMN, 
                    MOVER_COLUMN, 
                    URI_COLUMN
                ],
            };
            var dataTable = new YAHOO.widget.DataTable("schedule-table",
                columns, dataSource,
                { 
                    selectionMode:"single",
                    scrollable:true,
                }
            );
            return {
                oDs: dataSource,
                oDt: dataTable
            }
        }();
    });
    
}();
