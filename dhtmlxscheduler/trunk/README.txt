

This package includes version 3.6 of dhtmlxscheduler.

This software is allowed to be use under GPL. You need to obtain Commercial or Enterise License
to use it in non-GPL projects. Please contact sales@dhtmlx.com for details

CHANGES
-------
*1.0.3*
- Updating to dhtmlxscheduler 3.6

*1.0.2*
- Updating to dhtmlxscheduler 3.5
- Factoring out themes into includable resources

*1.0.1*
- Adding missing dhtmlxscheduler resource bundles - PDF, Weeek Agenda, Offline and Mobile CSS.
- Corrrecting various resource conditions not debug/no-debug modes
  - Fixes issue where source (uncompressed) resources would be loaded in debug mode(and vice versa)
- Adding symbolic link in sources folder to point to images directory in codebase.
  - Fixes issue with inaccessible image resources in debug mode


PATCHES
-------
Applied patch described here http://forum.dhtmlx.com/viewtopic.php?f=6&t=13809&start=50 
so that dataprocessor works properly in debug mode.
Added locale_recurring.js
Added Kiswahili translations
