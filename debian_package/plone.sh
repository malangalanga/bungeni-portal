#!/bin/bash

. _bashtasklog.sh
. _debpackfunctions.sh

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[Plone] Getting revision information..."

PLONE_CFG=$(getini deb.ini plone cfg)
PLONE_VERSION=$(getproperty ${PLONE_CFG} Plone)
logger.printTask "[Plone] Version ${PLONE_VERSION}"

PLONE_DIR=$(getini deb.ini plone dir)
PLONE_REVISION=$(getrevinfo ${PLONE_DIR})
logger.printTask "[Plone] Revision ${PLONE_REVISION}"

PLONE_BUILD_DATE=$(getdate)
PLONE_RELEASE_NAME="${PLONE_VERSION}+${PLONE_REVISION}-${PLONE_BUILD_DATE}"
PLONE_ZIP_FILE="plone_${PLONE_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[Plone] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[Plone] Zipping..."
{
	printf "\n\n"
		
	tar czf plone/$PLONE_ZIP_FILE $PLONE_DIR
	} &>> $CURR_DEB_LOG

logger.printTask "[Plone] Preparing debian pack folder..."
cd plone && ./prepare_debpackfolder.sh $PLONE_RELEASE_NAME $PLONE_ZIP_FILE $OS_ARCH_TYPE

