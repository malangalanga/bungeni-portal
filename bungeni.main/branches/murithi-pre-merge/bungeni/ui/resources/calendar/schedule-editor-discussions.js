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
var BODY_TEXT_COLUMN = "body_text";
var DIALOG_CONFIG = {
        width: "auto",
        fixedcenter: true,
        modal: true,
        visible: false,
        draggable: false,
        underlay: "none",
}

YAHOO.bungeni.Utils = function(){
    /**
     * @function wrapText
     * @description returns text as html wrapped in el tags
     */
    var wrapText = function(text, el){
        var _el = el || "em";
        return "<" + _el + ">" + text + "</" + _el + ">";
    }
    return {
        wrapText: wrapText
    }
}();

YAHOO.bungeni.formatters = function(){
    /**
     * @method itemTypeFormatter
     * @description render item type in reduced form
     */
     var BungeniUtils = YAHOO.bungeni.Utils;
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
             el.innerHTML = BungeniUtils.wrapText(rec_data.item_title);
         }else{
             if (rec_data.item_uri){
                el.innerHTML = (rec_data.item_title + 
                    "<em style='display:block;'><span>" +
                    scheduler_globals.text_moved_by + " : " + 
                    rec_data.item_mover + "</span>&nbsp;&nbsp;" +
                    "<a href='" + rec_data.item_uri + "'>" + 
                    scheduler_globals.text_action_view + "</a>"
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
    
    var countFormatter = function(el, record, column, data){
        el.innerHTML = this.getTrIndex(record)+1;
    }
    
    var longTextFormatter = function(el, record, column, data){
        var text = (record.getData()[column.key] || 
            scheduler_globals.column_discussion_text_missing
        );
        el.innerHTML = BungeniUtils.wrapText(text);
    }

    var editButtonFormatter = function(el, record, column, data){
        var button = new YAHOO.widget.Button({
            label: scheduler_globals.column_discussion_edit_button,
            id: el.id + ""
        });
        button.appendTo(el);
    }

    return {
     titleFormatter: itemTitleFormatter,
     typeFormatter: itemTypeFormatter,
     moveUpFormatter: itemMoveUpFormatter,
     moveDownFormatter: itemMoveDownFormatter,
     countFormatter: countFormatter,
     longTextFormatter: longTextFormatter,
     editButtonFormatter: editButtonFormatter
    }
}();

YAHOO.bungeni.scheduling = function(){
    var Event = YAHOO.util.Event;
    var BungeniUtils = YAHOO.bungeni.Utils;
    var handlers = function(){
        var renderDiscussionsTable = function(){
            var dataTable = YAHOO.bungeni.schedule.oDt;
            var index = dataTable.getSelectedRows()[0];
            var oData = dataTable.getRecord(index).getData();
            var discussions_url = ("./items/" + 
                oData.object_id + scheduler_globals.discussion_items_json_url
            );
            //render editor
            var editorContainer = document.createElement("div");
            var editorTextArea = document.createElement("textarea");
            editorTextArea.id = "discussion-editor-rte";
            editorContainer.appendChild(editorTextArea);
            Event.onAvailable("discussion-editor-rte", function(event){
                var editor = new YAHOO.widget.Editor("discussion-editor-rte",
                    { width:"100%", autoHeight: false }
                );
                editor.render();
            });
            this.body.appendChild(editorContainer);
            
            //render discussions data table
            var dataSource = YAHOO.util.DataSource(discussions_url);
            dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
            var container = document.createElement("div");
            this.body.appendChild(container);
            dataSource.responseSchema = {
                resultsList: "nodes",
                fields: [ OBJECT_ID_COLUMN, BODY_TEXT_COLUMN ]
            }
            var columns = [
                {
                    key: "number",
                    label: "",
                    formatter: YAHOO.bungeni.formatters.countFormatter
                },
                {
                    key: BODY_TEXT_COLUMN,
                    label: scheduler_globals.column_discussion_text,
                    formatter: YAHOO.bungeni.formatters.longTextFormatter
                },
                {
                    key: "edit_discussion",
                    label: "",
                    formatter: YAHOO.bungeni.formatters.editButtonFormatter
                }
            ]
            var dDt = new YAHOO.widget.DataTable(container, columns,
                dataSource,
                {
                    selectionMode: "single",
                    initialLoad: true
                }
            );
            dDt.subscribe("rowClickEvent", dDt.onEventSelectRow);
            dDt.subscribe("rowMouseoverEvent", dDt.onEventHighlightRow);
            dDt.subscribe("rowMouseoutEvent", dDt.onEventUnhighlightRow);
        }
        var showDiscussions = function(args){
            var dlg_id = "dlg-" + args.el.id;
            var dialog = new YAHOO.widget.SimpleDialog(dlg_id,
                DIALOG_CONFIG
            );
            var dialogButtons = [
                {
                    text: scheduler_globals.text_dialog_confirm_action,
                    handler: null
                },
                {
                    text: scheduler_globals.text_dialog_cancel_action,
                    handler: function(){ this.hide(); }
                },
            ]
            dialog.cfg.queueProperty("width", "500px");
            dialog.cfg.queueProperty("height", "400px");
            dialog.cfg.queueProperty("buttons", dialogButtons);
            dialog.setBody('');
            dialog.showEvent.subscribe(renderDiscussionsTable);
            dialog.setHeader(scheduler_globals.schedule_discussions_title);
            dialog.render(document.body);
            dialog.show();
            dialog.bringToTop();
        };
        return {
            showDiscussions: showDiscussions
        }
    }();
    Event.onDOMReady(function(){
        var layout = new YAHOO.widget.Layout("scheduler-layout",
            {
                height: 600,
                units: [
                    {
                        position:'top',
                        body: BungeniUtils.wrapText(
                            scheduler_globals.schedule_discussions_title, "h2"
                        ),
                        gutter: "2 2",
                        height: 42
                    },
                    {
                        position:'center',
                        body: '',
                        gutter: "2 2",
                    },
                ]
            }
        );
        layout.on("render", function(){
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
                var tableContainer = document.createElement("div");
                layout.getUnitByPosition("center").body.appendChild(tableContainer);
                var dataTable = new YAHOO.widget.DataTable(
                    tableContainer,
                    columns, dataSource,
                    {
                        caption: "hold down CONTROL key to select multiple items",
                        summary: "hold down CONTROL key to select multiple items",
                        selectionMode:"single",
                        scrollable:true,
                        width:"100%"
                    }
                );
                dataTable.subscribe("rowClickEvent", dataTable.onEventSelectRow);
                dataTable.subscribe("rowMouseoverEvent", 
                    dataTable.onEventHighlightRow
                );
                dataTable.subscribe("rowMouseoutEvent", 
                    dataTable.onEventUnhighlightRow
                );
                dataTable.subscribe("rowSelectEvent",
                    YAHOO.bungeni.scheduling.handlers.showDiscussions
                )
                
                return {
                    oDs: dataSource,
                    oDt: dataTable
                }
            }();
        });
        layout.render();
    });
    return {
        handlers: handlers
    }
}();
