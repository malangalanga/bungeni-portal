#!/bin/bash

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
logger.printTask "[Portal] Version ${PLONE_VERSION}"

PORTAL_DIR=$(getini deb.ini portal dir)
PORTAL_REVISION=$(getrevinfo ${PORTAL_DIR})
logger.printTask "[Portal] Revision ${PORTAL_REVISION}"

PORTAL_BUILD_DATE=$(getdate)
PORTAL_RELEASE_NAME="${PORTAL_VERSION}+${PORTAL_REVISION}-${PORTAL_BUILD_DATE}"
PORTAL_ZIP_FILE="portal_${PORTAL_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[Portal] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[Portal] Zipping..."
{
	printf "\n\n"
		
	tar czf portal/$PORTAL_ZIP_FILE $PORTAL_DIR
	} &>> $CURR_DEB_LOG

logger.printTask "[Portal] Preparing debian pack folder..."
cd portal && ./prepare_debpackfolder.sh $PORTAL_RELEASE_NAME $PORTAL_ZIP_FILE $OS_ARCH_TYPE
