#!/bin/bash
#===============================================================================
#
#          FILE:  portal.sh
#
#         USAGE:  ./portal.sh
#
#   DESCRIPTION:  Creates portal debian package
#	
#
#       OPTIONS:  ---
#          BUGS:  ---
#         NOTES:  ---
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh	
#				  portal/prepare_debpackfolder.sh	

#       AUTHORS:  Ashok Hariharan <ashok@parliaments.info>
#				  Samuel Weru <samweru@gmail.com>

#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

. _bashtasklog.sh
. _debpackfunctions.sh

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[Portal] Getting revision information..."

PORTAL_CFG=$(getini deb.ini portal cfg)
PORTAL_VERSION=$(getproperty ${PORTAL_CFG} Deliverance)
if [ ! -z $PORTAL_VERSION ] ; then
	logger.printTask "[Portal] Deliverance Version ${PORTAL_VERSION}"
else
	logger.printFail "[Portal] Deliverance Version Unavailable"
fi

PORTAL_DIR=$(getini deb.ini portal dir)
PORTAL_REVISION=$(getrevinfo ${PORTAL_DIR})
if [ ! -z $PORTAL_REVISION ] ; then
	logger.printTask "[Portal] Revision ${PORTAL_REVISION}"
else
	logger.printFail "[Portal] Revision Unavailable"
fi

PORTAL_BUILD_DATE=$(getdate)
PORTAL_RELEASE_NAME="${PORTAL_VERSION}+${PORTAL_REVISION}-${PORTAL_BUILD_DATE}"
PORTAL_ZIP_FILE="portal_${PORTAL_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[Portal] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[Portal] Zipping..."
{
	printf "\n\n"
		
	tar -czf portal/$PORTAL_ZIP_FILE -T portal.include -X portal.exclude
	} &>> $CURR_DEB_LOG

logger.printTask "[Portal] Preparing debian pack folder..."
cd portal && ./prepare_debpackfolder.sh $PORTAL_RELEASE_NAME $PORTAL_ZIP_FILE $OS_ARCH_TYPE
