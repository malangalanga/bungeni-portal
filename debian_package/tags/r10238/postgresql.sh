#!/bin/bash

. _bashtasklog.sh
. _debpackfunctions.sh

#set -x

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

POSTGRES_VERSION=$1
logger.printTask "[PostgreSQL] Version ${POSTGRES_VERSION}"

POSTGRES_BUILD_DATE=$(getdate)
POSTGRES_RELEASE_NAME="${POSTGRES_VERSION}+${POSTGRES_BUILD_DATE}"
POSTGRES_ZIP_FILE="postgresql_${POSTGRES_RELEASE_NAME}.tar.gz"

OS_ARCH_TYPE=$(getarchtype)
logger.printTask "[PostgreSQL] Architecture Type ${OS_ARCH_TYPE}"

logger.printTask "[PostgreSQL] Zipping..."
{
	printf "\n\n"
		
	tar -czf postgresql/$POSTGRES_ZIP_FILE -T postgresql.include -X postgresql.exclude
	} &>> $CURR_DEB_LOG

logger.printTask "[PostgreSQL] Preparing debian pack folder..."
cd postgresql && ./prepare_debpackfolder.sh $POSTGRES_RELEASE_NAME $POSTGRES_ZIP_FILE $OS_ARCH_TYPE
