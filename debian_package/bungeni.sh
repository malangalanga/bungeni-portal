#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version> <release> <archtype>"
 exit 65
fi

BUNGENI_ZIP_FILE="bungeni_$1+$2.tar.gz"
BUNGENI_APPS_HOME="/opt/bungeni/bungeni_apps"

echo "Zipping bungeni"
tar cvzf bungeni/$BUNGENI_ZIP_FILE /opt/bungeni --exclude=$BUNGENI_APPS_HOME/exist* --exclude=$BUNGENI_APPS_HOME/glue* --exclude=$BUNGENI_APPS_HOME/jython* --exclude=$BUNGENI_APPS_HOME/bungeni/plone* --exclude=$BUNGENI_APPS_HOME/.* --exclude=$BUNGENI_APPS_HOME/config/xml*

cd bungeni && ./prepare_debpackfolder.sh $1+$2 $BUNGENI_ZIP_FILE $3
