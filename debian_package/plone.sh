#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version> <release> <archtype>"
 exit 65
fi

PLONE_ZIP_FILE="plone_$1+$2.tar.gz"

echo "Zipping plone"
tar cvzf plone/$PLONE_ZIP_FILE /opt/bungeni/bungeni_apps/bungeni/plone

cd plone && ./prepare_debpackfolder.sh $1+$2 $PLONE_ZIP_FILE $3
