/*
dhtmlxScheduler v.2.3

This software is allowed to use under GPL or you need to obtain Commercial or Enterise License
to use it in not GPL project. Please contact sales@dhtmlx.com for details

(c) DHTMLX Ltd.
*/
scheduler.config.limit_start=new Date(-3999,0,0);scheduler.config.limit_end=new Date(3999,0,0);scheduler.config.limit_view=false;(function(){var B=null;scheduler.attachEvent("onBeforeViewChange",function(E,D,C,F){F=F||D;C=C||E;if(scheduler.config.limit_view){if(F.valueOf()>scheduler.config.limit_end.valueOf()||this.date.add(F,1,C)<=scheduler.config.limit_start.valueOf()){setTimeout(function(){scheduler.setCurrentView(scheduler._date,C)},1);return false}}return true});var A=function(D){var E=scheduler.config;var C=(D.start_date.valueOf()>=E.limit_start.valueOf()&&D.end_date.valueOf()<=E.limit_end.valueOf());if(!C){scheduler._drag_id=null;scheduler._drag_mode=null;scheduler.callEvent("onLimitViolation",[D.id,D])}return C};scheduler.attachEvent("onBeforeDrag",function(C){if(!C){return true}return A(scheduler.getEvent(C))});scheduler.attachEvent("onClick",function(D,C){return A(scheduler.getEvent(D))});scheduler.attachEvent("onBeforeLightbox",function(D){var C=scheduler.getEvent(D);B=[C.start_date,C.end_date];return A(C)});scheduler.attachEvent("onEventAdded",function(D){if(!D){return true}var C=scheduler.getEvent(D);if(!A(C)){if(C.start_date<scheduler.config.limit_start){C.start_date=new Date(scheduler.config.limit_start)}if(C.end_date>scheduler.config.limit_end){C.end_date=new Date(scheduler.config.limit_end);C._timed=this.is_one_day_event(C)}if(C.start_date>C.end_date){C.end_date=this.date.add(C.start_date,(this.config.event_duration||this.config.time_step),"minute")}}return true});scheduler.attachEvent("onEventChanged",function(D){if(!D){return true}var C=scheduler.getEvent(D);if(!A(C)){if(!B){return false}C.start_date=B[0];C.end_date=B[1];C._timed=this.is_one_day_event(C)}return true});scheduler.attachEvent("onBeforeEventChanged",function(D,C,E){return A(D)})})();