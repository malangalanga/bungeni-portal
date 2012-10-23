#!/bin/bash

echo "Getting portal revision information..."
PORTAL_DIR="/opt/bungeni/bungeni_apps/bungeni/portal"
PORTAL_VERSION=$(grep "Deliverance" $PORTAL_DIR/versions.cfg | cut -d "=" -f2 | tr -d '[:space:]')
PORTAL_REVISION=$(svn info $PORTAL_DIR |grep Revision: |cut -c11-)
PORTAL_REVISION_DATE=$(svn info $PORTAL_DIR |grep 'Last Changed Date:' |cut -d " " -f4)
PORTAL_ZIP_FILE="portal_$PORTAL_VERSION+$PORTAL_REVISION-$PORTAL_REVISION_DATE.tar.gz"

echo "Zipping portal"
tar cvzf portal/$PORTAL_ZIP_FILE $PORTAL_DIR

echo "Get Architecture Type"
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd portal && ./prepare_debpackfolder.sh $PORTAL_VERSION+$PORTAL_REVISION-$PORTAL_REVISION_DATE $PORTAL_ZIP_FILE $ARCHTYPE
