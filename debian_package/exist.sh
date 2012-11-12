#!/bin/bash

. _bashtasklog.sh
. _debpackfunctions.sh

#set -x verbose

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[ExistDb] Getting version information..."
BUNGENI_APPS_HOME=$(getini deb.ini global apps_home)
EXIST_PROPERTIES=$(getini deb.ini exist properties)

EXIST_VERSION=$(getproperty ${EXIST_PROPERTIES} project.version.numeric)
logger.printTask "[ExistDb] Version ${EXIST_VERSION}"

EXIST_RELEASE=$1
logger.printTask "[ExistDb] Release ${EXIST_RELEASE}"

EXIST_BUILD_DATE=$(getdate)
EXIST_RELEASE_NAME="${EXIST_VERSION}+${EXIST_RELEASE}-${EXIST_BUILD_DATE}"
EXIST_ZIP_FILE="exist-db_${EXIST_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[ExistDb] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[ExistDb] Zipping ..."
{	
	printf "\n\n"
	
	tar czf exist/$EXIST_ZIP_FILE /opt/bungeni \
	--exclude=$BUNGENI_APPS_HOME/bungeni* \
	--exclude=$BUNGENI_APPS_HOME/logs* \
	--exclude=$BUNGENI_APPS_HOME/pid* \
	--exclude=$BUNGENI_APPS_HOME/config/glue.ini \
	--exclude=$BUNGENI_APPS_HOME/config/supervisord.conf \
	--exclude=$BUNGENI_APPS_HOME/python* \
	--exclude=/opt/bungeni/exec* \
	--exclude=$BUNGENI_APPS_HOME/.* \
	--exclude=/opt/bungeni/.* \
	--exclude=/opt/bungeni/log.txt \
	--exclude=$BUNGENI_APPS_HOME/rabbitmq* 
	
	} &>> $CURR_DEB_LOG

logger.printTask "[ExistDb] Preparing debian pack folder..."
cd exist && ./prepare_debpackfolder.sh $EXIST_RELEASE_NAME $EXIST_ZIP_FILE $OS_ARCH_TYPE
