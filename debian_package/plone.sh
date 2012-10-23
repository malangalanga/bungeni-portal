#!/bin/bash

echo "Getting plone revision information..."
PLONE_DIR="/opt/bungeni/bungeni_apps/bungeni/plone"
PLONE_VERSION=$(grep "Plone" $PLONE_DIR/versions.cfg | awk "NR==2" | cut -d "=" -f2 | tr -d '\r|[:space:]')
PLONE_REVISION=$(svn info $PLONE_DIR |grep Revision: |cut -c11-)
PLONE_REVISION_DATE=$(svn info $PLONE_DIR |grep 'Last Changed Date:' |cut -d " " -f4)
PLONE_ZIP_FILE="plone_$PLONE_VERSION+$PLONE_REVISION-$PLONE_REVISION_DATE.tar.gz"

echo "Zipping plone"
tar cvzf plone/$PLONE_ZIP_FILE $PLONE_DIR

echo "Get Architecture Type"
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd plone && ./prepare_debpackfolder.sh $PLONE_VERSION+$PLONE_REVISION-$PLONE_REVISION_DATE $PLONE_ZIP_FILE $ARCHTYPE
