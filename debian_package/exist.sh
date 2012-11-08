#!/bin/bash

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release>"
 exit 65
fi

echo "[Exist $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Getting version information..."
BUILD_DATE=$(date +"%Y%m%d")
BUNGENI_APPS_HOME="/opt/bungeni/bungeni_apps"
EXIST_VERSION=$(cat $BUNGENI_APPS_HOME/exist/build.properties | grep project.version.numeric | cut -d "=" -f 2 | tr -d '\r|[:space:]')
EXIST_ZIP_FILE="exist-db_${EXIST_VERSION}+$1-$BUILD_DATE.tar.gz"

echo "[Exist $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Zipping ..."
tar czf exist/$EXIST_ZIP_FILE /opt/bungeni --exclude=$BUNGENI_APPS_HOME/bungeni* --exclude=$BUNGENI_APPS_HOME/logs* --exclude=$BUNGENI_APPS_HOME/pid* --exclude=$BUNGENI_APPS_HOME/config/glue.ini --exclude=$BUNGENI_APPS_HOME/config/supervisord.conf --exclude=$BUNGENI_APPS_HOME/python* --exclude=/opt/bungeni/exec* --exclude=$BUNGENI_APPS_HOME/.* --exclude=/opt/bungeni/.* --exclude=/opt/bungeni/log.txt --exclude=$BUNGENI_APPS_HOME/rabbitmq*

echo "[Exist $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Get architecture type"
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd exist && ./prepare_debpackfolder.sh $EXIST_VERSION+$1-$BUILD_DATE $EXIST_ZIP_FILE $ARCHTYPE
