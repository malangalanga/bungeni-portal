#!/bin/bash

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version>"
 exit 65
fi

echo "Getting bungeni revision information..."
BUNGENI_APPS_HOME="/opt/bungeni/bungeni_apps"
BUNGENI_REVISION=$(svn info $BUNGENI_APPS_HOME/bungeni |grep Revision: |cut -c11-)
BUNGENI_REVISION_DATE=$(svn info $BUNGENI_APPS_HOME/bungeni |grep 'Last Changed Date:' |cut -d " " -f 4)
BUNGENI_ZIP_FILE="bungeni_$1+$BUNGENI_REVISION-$BUNGENI_REVISION_DATE.tar.gz"

echo "Zipping bungeni"
tar cvzf bungeni/$BUNGENI_ZIP_FILE /opt/bungeni --exclude=$BUNGENI_APPS_HOME/exist* --exclude=$BUNGENI_APPS_HOME/glue* --exclude=$BUNGENI_APPS_HOME/jython* --exclude=$BUNGENI_APPS_HOME/bungeni/plone* --exclude=$BUNGENI_APPS_HOME/bungeni/portal* --exclude=$BUNGENI_APPS_HOME/.* --exclude=$BUNGENI_APPS_HOME/config/xml*

echo "Get Architecture Type"
if [ $(getconf LONG_BIT) == 64 ]
then
	ARCHTYPE="amd64"
else
	ARCHTYPE="i386"
fi

cd bungeni && ./prepare_debpackfolder.sh $1+$BUNGENI_REVISION-$BUNGENI_REVISION_DATE $BUNGENI_ZIP_FILE $ARCHTYPE
