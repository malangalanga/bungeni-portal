#!/bin/bash
#===============================================================================
#
#          FILE:  bungeni.sh
#
#         USAGE:  sudo ./bungeni.sh <version>
#
#   DESCRIPTION:  Creates bungeni debian package
#
#  REQUIREMENTS:  Run as sudo user		
#
#       OPTIONS:  ---
#          BUGS:  ---
#         NOTES:  ---
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh	
#				  bungeni/prepare_debpackfolder.sh	

#       AUTHORS:  Ashok Hariharan <ashok@parliaments.info>
#				  Samuel Weru <samweru@gmail.com>

#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

. _bashtasklog.sh
. _debpackfunctions.sh

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[Bungeni] Getting version information..."
BUNGENI_DIR=$(getini deb.ini bungeni dir)

BUNGENI_VERSION=$1
logger.printTask "[Bungeni] Version ${BUNGENI_VERSION}"

BUNGENI_REVISION=$(getrevinfo $BUNGENI_DIR)
if [ ! -z $BUNGENI_REVISION ] ; then
	logger.printTask "[Bungeni] Revision ${BUNGENI_REVISION}"
else
	logger.printFail "[Bungeni] Revision Unavailable"
fi

BUNGENI_BUILD_DATE=$(getdate)
BUNGENI_RELEASE_NAME="${BUNGENI_VERSION}+${BUNGENI_REVISION}-${BUNGENI_BUILD_DATE}"
BUNGENI_ZIP_FILE="bungeni_${BUNGENI_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[Bungeni] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[Bungeni] Zipping ..."
{
	printf "\n\n"
	
	tar -czf bungeni/$BUNGENI_ZIP_FILE -T bungeni.include -X bungeni.exclude
	} &>> $CURR_DEB_LOG

logger.printTask "[Bungeni] Preparing debian pack folder..."
cd bungeni && ./prepare_debpackfolder.sh $BUNGENI_RELEASE_NAME $BUNGENI_ZIP_FILE $OS_ARCH_TYPE
