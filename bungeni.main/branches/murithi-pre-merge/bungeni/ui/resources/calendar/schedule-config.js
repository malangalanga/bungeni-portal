/**
 * Resusable configurations used by various Bungeni scheduling bundles
 * 
 * Defines the bungeni namespace and configuration components
**/
YAHOO.namespace("bungeni");

YAHOO.bungeni.config = function(){
    var lang = YAHOO.lang;
    var scheduling_configs = {
        columns : {
            ID_COLUMN : "item_id",
            OBJECT_ID_COLUMN : "object_id",
            TYPE_COLUMN : "item_type",
            TITLE_COLUMN : "item_title",
            MOVE_UP_COLUMN : "item_move_up",
            MOVE_DOWN_COLUMN : "item_move_down",
            MOVER_COLUMN : "item_mover",
            URI_COLUMN : "item_uri",
        },
        formatters: {
            viewLink : function(el, oRecord, oColumn, oData, oDataTable) {
                if(lang.isString(oData) && (oData > "")) {
                    el.innerHTML = ("<a href=\"" + oData + "target=\"blank\"\">" + 
                        scheduler_globals.text_action_view + "</a>"
                    );
                }
                else {
                    el.innerHTML = lang.isValue(oData) ? oData : "";
                }
            },
        }
    }
    return {
        scheduling: scheduling_configs,
    }
}();
