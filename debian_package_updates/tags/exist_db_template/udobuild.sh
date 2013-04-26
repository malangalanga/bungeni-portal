#!/bin/bash
#===============================================================================
#
#          FILE:  udobuild.sh
#
#         USAGE:  ./udobuild.sh
#
#   DESCRIPTION:  build update
#
#       OPTIONS:  ---
#          BUGS:  ---
#         NOTES:  ---
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh		
#        AUTHOR:  Samuel Weru, samweru@gmail.com
#       COMPANY:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

. _bashtasklog.sh
. _debpackfunctions.sh

new bashtasklog logger

logger.printTask "Extracting latest and previous releases..."	
./udoxtract.sh
logger.printTask "Doing diff between latest and previous releases..."	
./udodiff.sh
logger.printTask "Generating debian package update.."	
./udogetup.sh
logger.printOk "Done."
