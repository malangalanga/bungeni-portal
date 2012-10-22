#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version> <release> <archtype>"
 exit 65
fi

PORTAL_ZIP_FILE="portal_$1+$2.tar.gz"

echo "Zipping portal"
tar cvzf portal/$PORTAL_ZIP_FILE /opt/bungeni/bungeni_apps/bungeni/portal --exclude=/opt/bungeni/bungeni_apps/bungeni/portal/develop-eggs*

cd portal && ./prepare_debpackfolder.sh $1+$2 $PORTAL_ZIP_FILE $3
