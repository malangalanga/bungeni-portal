#!/bin/bash

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <archtype>"
 exit 65
fi

echo "Getting portal revision information..."
PORTAL_DIR="/opt/bungeni/bungeni_apps/bungeni/portal"
PORTAL_VERSION=$(grep "Deliverance" $PORTAL_DIR/versions.cfg | cut -d "=" -f2 | tr -d '[:space:]')
PORTAL_REVISION=$(svn info $PORTAL_DIR |grep Revision: |cut -c11-)
PORTAL_REVISION_DATE=$(svn info $PORTAL_DIR |grep 'Last Changed Date:' |cut -d " " -f4)
PORTAL_ZIP_FILE="portal_$PORTAL_VERSION+$PORTAL_REVISION-$PORTAL_REVISION_DATE.tar.gz"

echo "Zipping portal"
tar cvzf portal/$PORTAL_ZIP_FILE $PORTAL_DIR

cd portal && ./prepare_debpackfolder.sh $PORTAL_VERSION+$PORTAL_REVISION-$PORTAL_REVISION_DATE $PORTAL_ZIP_FILE $1
