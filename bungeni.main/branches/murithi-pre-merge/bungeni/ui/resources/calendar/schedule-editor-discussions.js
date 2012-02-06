/**
 * This module renders UI components that hadle editing of minutes.
**/
var DIALOG_CONFIG = {
        width: "auto",
        fixedcenter: true,
        modal: true,
        visible: false,
        draggable: false,
        underlay: "none",
}
var MODE_ADD = "MODE_ADD";
var MODE_EDIT = "MODE_EDIT";

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
     var Columns = YAHOO.bungeni.config.scheduling.columns;
     var itemTypeFormatter = function(el, record, column, data){
         el.innerHTML = ("<span style='font-size:10px;'>" + 
            record.getData()[Columns.TYPE_COLUMN] + 
            "</span>"
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
        if (!el.innerHTML){
            var button = new YAHOO.widget.Button({
                label: scheduler_globals.column_discussion_edit_button,
                id: el.id + "-edit-button"
            });
            button.appendTo(el);
        }
    }

    var deleteButtonFormatter = function(el, record, column, data){
        if (!el.innerHTML){
            var button = new YAHOO.widget.Button({
                label: scheduler_globals.column_discussion_delete_button,
                id: el.id + "-delete-button"
            });
            button.appendTo(el);
        }
    }

    return {
     titleFormatter: itemTitleFormatter,
     typeFormatter: itemTypeFormatter,
     moveUpFormatter: itemMoveUpFormatter,
     moveDownFormatter: itemMoveDownFormatter,
     countFormatter: countFormatter,
     longTextFormatter: longTextFormatter,
     editButtonFormatter: editButtonFormatter,
     deleteButtonFormatter: deleteButtonFormatter
    }
}();

YAHOO.bungeni.scheduling = function(){
    var Event = YAHOO.util.Event;
    var YJSON = YAHOO.lang.JSON;
    var YCM = YAHOO.util.Connect;
    var BungeniUtils = YAHOO.bungeni.Utils;
    var Columns = YAHOO.bungeni.config.scheduling.columns;
    
    var dialogs = function(){
        var blocking = {
            init: function(){
                this.dialog = new YAHOO.widget.SimpleDialog(
                    "scheduling-blocking", DIALOG_CONFIG
                );
                this.dialog.setHeader(scheduler_globals.saving_dialog_header);
                this.dialog.setBody("");
                this.dialog.cfg.queueProperty("width", "200px");
                this.dialog.cfg.queueProperty("close", false);
                this.dialog.cfg.queueProperty("icon",
                    YAHOO.widget.SimpleDialog.ICON_BLOCK
                );
                this.dialog.render(document.body);
            },
            show: function(message){
                if(!this.dialog){
                    this.init();
                }
                this.dialog.setBody(message);
                this.dialog.show();
                this.dialog.bringToTop();
            },
            hide: function(){
                this.dialog.hide();
            }
        }
        var confirm = {
            init: function(){
                var buttons = [
                    {
                        text: scheduler_globals.delete_dialog_confirm,
                        handler: function(){ 
                            this._parent.confirm_callback();
                            this._parent.confirm_callback = null;
                            this.hide();
                        }
                    },
                    {
                        text: scheduler_globals.delete_dialog_cancel,
                        handler: function(){ 
                            this._parent.confirm_callback = null;
                            this.hide(); 
                        },
                        default: true
                    },
                ];
                this.dialog = new YAHOO.widget.SimpleDialog(
                    "scheduling-confirm", DIALOG_CONFIG
                );
                this.dialog._parent = this;
                this.dialog.setHeader(scheduler_globals.confirm_dialog_title);
                this.dialog.setBody("");
                this.dialog.cfg.queueProperty("width", "200px");
                this.dialog.cfg.queueProperty("buttons", buttons);
                this.dialog.render(document.body);
            },
            show: function(message, confirm_callback){
                if(!this.dialog){
                    this.init();
                }
                this.confirm_callback = confirm_callback;
                this.dialog.setBody(message);
                this.dialog.show();
                this.dialog.bringToTop();
            },
            hide: function(){
                this.callback = null;
                this.dialog.hide();
            }
        }
        return {
            blocking: blocking,
            confirm: confirm
        }
    }();
    
    var discussionEditor = function(){
        init = function(){
           this.dialog = new YAHOO.widget.SimpleDialog("discussion-editor",
                DIALOG_CONFIG
            );
            this.dialog._parent = this
            var dialogButtons = [
                {
                    text: scheduler_globals.save_discussion_button_text,
                    handler: function(){
                        var text = this._parent.getText();
                        var mode = this._parent.mode;
                        var cDt = this._parent.dataTable;
                        if (text){
                            if (mode == MODE_ADD){
                                var new_record = {};
                                new_record[Columns.BODY_TEXT_COLUMN] = text;
                                cDt.addRow(new_record);
                            }else{
                                var index = cDt.getSelectedRows()[0];
                                if(index){
                                    var record = cDt.getRecord(index);
                                    var data = record.getData();
                                    data[Columns.BODY_TEXT_COLUMN] = text;
                                    cDt.updateRow(index, data);
                                }
                            }
                            this.hide();
                        }
                    }
                },
                {
                    text: scheduler_globals.text_dialog_cancel_action,
                    handler: function(){ this.hide(); }
                },
            ]
            this.dialog.cfg.queueProperty("width", "500px");
            this.dialog.cfg.queueProperty("height", "400px");
            this.dialog.cfg.queueProperty("buttons", dialogButtons);
            this.dialog.setBody("<div><textarea name='discussiontext' id='discussiontext'></textarea></div>");
            this.dialog.setHeader(scheduler_globals.schedule_discussions_title);
            this.dialog.render(document.body);
            Event.onAvailable("discussiontext", function(e){
                var editor = new YAHOO.widget.Editor("discussiontext",
                    { width:"100%", height:"150px" ,autoHeight: false }
                );
                editor.render();
                YAHOO.bungeni.scheduling.discussionEditor.getText = function(){
                    return editor.cleanHTML(editor.getEditorHTML())
                }
                YAHOO.bungeni.scheduling.discussionEditor.setText = function(text){
                    editor.setEditorHTML(text);
                }
            });
        }
        render = function(dataTable, mode){
            this.dataTable = dataTable;
            this.mode = mode || MODE_ADD;
            this.mode
            if (!this.dialog){
                this.init();
            }
            this.dialog.show();
        }
        var RequestObject = {
            handleSuccess: function(o){
                YAHOO.bungeni.scheduling.dialogs.blocking.hide();
            },
            handleFailure: function(o){
            },
            startRequest: function(data){
                var scheduled_item_id = YAHOO.bungeni.schedule.oDt.getRecord(
                    YAHOO.bungeni.schedule.oDt.getSelectedRows()[0]
                ).getData()[Columns.OBJECT_ID_COLUMN];
                var save_url = ("./items/" + scheduled_item_id + 
                    scheduler_globals.discussions_save_url
                );
                Event.stopEvent(window.event);
                YAHOO.bungeni.scheduling.dialogs.blocking.show(
                    scheduler_globals.saving_discussions_text
                );
                YCM.asyncRequest("POST", save_url, callback, data);
                    
            }
        }
        
        var callback = {
            success: RequestObject.handleSuccess,
            failure: RequestObject.handleFailure,
            scope: RequestObject
        }

        return {
            init: init,
            render: render,
            SaveRequest: RequestObject
        }
    }();
    
    var handlers = function(){
        var renderDiscussionsTable = function(){
            var dataTable = YAHOO.bungeni.schedule.oDt;
            var index = dataTable.getSelectedRows()[0];
            var oData = dataTable.getRecord(index).getData();
            var discussions_url = ("./items/" + 
                oData.object_id + scheduler_globals.discussion_items_json_url
            );
                        
            //render discussions data table
            var dataSource = YAHOO.util.DataSource(discussions_url);
            dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
            var button_container = document.createElement("div");
            button_container.style.marginBottom = "1em";
            this.body.appendChild(button_container);
            var add_button = new YAHOO.widget.Button({
                label: scheduler_globals.add_discussion_button_text
            });
            add_button.appendTo(button_container);
            var container = document.createElement("div");
            this.body.appendChild(container);
            dataSource.responseSchema = {
                resultsList: "nodes",
                fields: [ Columns.OBJECT_ID_COLUMN, Columns.BODY_TEXT_COLUMN ]
            }
            var columns = [
                {
                    key: "number",
                    label: "",
                    formatter: YAHOO.bungeni.formatters.countFormatter
                },
                {
                    key: Columns.BODY_TEXT_COLUMN,
                    label: scheduler_globals.column_discussion_text,
                    formatter: YAHOO.bungeni.formatters.longTextFormatter
                },
                {
                    key: Columns.DISCUSSION_EDIT_COLUMN,
                    label: "",
                    formatter: YAHOO.bungeni.formatters.editButtonFormatter
                },
                {
                    key: Columns.DISCUSSION_DELETE_COLUMN,
                    label: "",
                    formatter: YAHOO.bungeni.formatters.deleteButtonFormatter
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
            dDt.subscribe("cellClickEvent", 
                YAHOO.bungeni.scheduling.handlers.editDiscussion
            );
            dDt.subscribe("cellClickEvent", 
                YAHOO.bungeni.scheduling.handlers.deleteDiscussion
            );
            add_button.on("click", function(){
                YAHOO.bungeni.scheduling.discussionEditor.render(dDt);
                YAHOO.bungeni.scheduling.discussionEditor.setText("");
            });
            YAHOO.bungeni.schedule.getDiscussionsDataTable = function(){
                return dDt;
            }
        }
        var showDiscussions = function(args){
            var dlg_id = "dlg-" + args.el.id;
            var dialog = new YAHOO.widget.SimpleDialog(dlg_id,
                DIALOG_CONFIG
            );
            var dialogButtons = [
                {
                    text: scheduler_globals.save_button_text,
                    handler: YAHOO.bungeni.scheduling.handlers.saveDiscussions
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
        var editDiscussion = function(args){
            var column = this.getColumn(args.target);
            if(column.field == Columns.DISCUSSION_EDIT_COLUMN){
                Event.stopEvent(args.event);
                YAHOO.bungeni.scheduling.discussionEditor.render(this, MODE_EDIT);
                YAHOO.bungeni.scheduling.discussionEditor.setText(
                    this.getRecord(args.target).getData()[Columns.BODY_TEXT_COLUMN] ||
                    ""
                );

            }
        }
        var deleteDiscussion = function(args){
            var column = this.getColumn(args.target);
            if(column.field == Columns.DISCUSSION_DELETE_COLUMN){
                var contextDt = this;
                var delete_callback = function(){
                    contextDt.deleteRow(
                        contextDt.getRecord(args.target)
                    );
                }
                YAHOO.bungeni.scheduling.dialogs.confirm.show(
                    scheduler_globals.confirm_message_delete_discussion,
                    delete_callback
                );
            }
        }
        var saveDiscussions = function(args){
            var dataTable = YAHOO.bungeni.schedule.getDiscussionsDataTable();
            var record_set = dataTable.getRecordSet();
            var records = record_set.getRecords();
            if (record_set.getLength()){
                var item_data = new Array();
                for (index in records){
                    var record_data = records[index].getData();
                    var save_data = {
                        object_id: record_data.object_id,
                        body_text: record_data.body_text,
                    }
                    item_data.push(save_data);
                }
                var post_data = "data=" + YJSON.stringify(item_data);
                YAHOO.bungeni.scheduling.discussionEditor.SaveRequest.startRequest(post_data);
            }
        }
        return {
            showDiscussions: showDiscussions,
            editDiscussion: editDiscussion,
            deleteDiscussion: deleteDiscussion,
            saveDiscussions: saveDiscussions
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
                        key:Columns.TYPE_COLUMN, 
                        label: scheduler_globals.column_type,
                        formatter: YAHOO.bungeni.formatters.typeFormatter,
                    },
                    {
                        key:Columns.TITLE_COLUMN, 
                        label: scheduler_globals.column_title,
                        formatter: YAHOO.bungeni.formatters.titleFormatter
                    },
                    {
                        key:Columns.MOVE_UP_COLUMN, 
                        label:"", 
                        formatter:YAHOO.bungeni.formatters.moveUpFormatter
                    },
                    {
                        key:Columns.MOVE_DOWN_COLUMN, 
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
                        Columns.ID_COLUMN, 
                        Columns.TITLE_COLUMN, 
                        Columns.TYPE_COLUMN, 
                        Columns.OBJECT_ID_COLUMN, 
                        Columns.MOVER_COLUMN, 
                        Columns.URI_COLUMN
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
        handlers: handlers,
        discussionEditor: discussionEditor,
        dialogs: dialogs
    }
}();
