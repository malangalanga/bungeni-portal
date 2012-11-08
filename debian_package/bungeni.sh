#!/bin/bash

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version> [<suffix>]"
 exit 65
fi

echo "[Bungeni $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Getting revision information..."
BUILD_DATE=$(date +"%Y%m%d")
BUNGENI_APPS_HOME="/opt/bungeni/bungeni_apps"
BUNGENI_REVISION=$(svn info $BUNGENI_APPS_HOME/bungeni |grep Revision: |cut -c11-)
BUNGENI_ZIP_FILE="bungeni_$1+$BUNGENI_REVISION-$BUILD_DATE.tar.gz"

echo "[Bungeni $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Zipping..."
tar czf bungeni/$BUNGENI_ZIP_FILE /opt/bungeni --exclude=$BUNGENI_APPS_HOME/exist* --exclude=$BUNGENI_APPS_HOME/glue* --exclude=$BUNGENI_APPS_HOME/jython* --exclude=$BUNGENI_APPS_HOME/bungeni/plone* --exclude=$BUNGENI_APPS_HOME/bungeni/portal* --exclude=$BUNGENI_APPS_HOME/.* --exclude=$BUNGENI_APPS_HOME/config/xml* --exclude=/opt/bungeni/.bungenitmp*

echo "[Bungeni $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Get architecture type."
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd bungeni && ./prepare_debpackfolder.sh $1+$BUNGENI_REVISION-$BUILD_DATE $BUNGENI_ZIP_FILE $ARCHTYPE
