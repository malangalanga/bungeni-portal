#!/bin/bash

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Getting revision information..."
BUILD_DATE=$(date +"%Y%m%d")
PLONE_DIR="/opt/bungeni/bungeni_apps/bungeni/plone"
PLONE_VERSION=$(grep "Plone" $PLONE_DIR/versions.cfg | awk "NR==2" | cut -d "=" -f2 | tr -d '\r|[:space:]')
PLONE_REVISION=$(svn info $PLONE_DIR |grep Revision: |cut -c11-)
PLONE_ZIP_FILE="plone_$PLONE_VERSION+$PLONE_REVISION-$BUILD_DATE.tar.gz"

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Zipping..."
tar czf plone/$PLONE_ZIP_FILE $PLONE_DIR

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Get architecture type"
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd plone && ./prepare_debpackfolder.sh $PLONE_VERSION+$PLONE_REVISION-$BUILD_DATE $PLONE_ZIP_FILE $ARCHTYPE
