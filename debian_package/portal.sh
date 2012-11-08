#!/bin/bash

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Getting revision information..."
BUILD_DATE=$(date +"%Y%m%d")
PORTAL_DIR="/opt/bungeni/bungeni_apps/bungeni/portal"
PORTAL_VERSION=$(grep "Deliverance" $PORTAL_DIR/versions.cfg | cut -d "=" -f2 | tr -d '[:space:]')
PORTAL_REVISION=$(svn info $PORTAL_DIR |grep Revision: |cut -c11-)
PORTAL_ZIP_FILE="portal_$PORTAL_VERSION+$PORTAL_REVISION-$BUILD_DATE.tar.gz"

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Zipping..."
tar czf portal/$PORTAL_ZIP_FILE $PORTAL_DIR

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Get architecture type."
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd portal && ./prepare_debpackfolder.sh $PORTAL_VERSION+$PORTAL_REVISION-$BUILD_DATE $PORTAL_ZIP_FILE $ARCHTYPE
