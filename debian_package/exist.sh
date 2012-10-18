#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version> <release> <archtype>"
 exit 65
fi

EXIST_ZIP_FILE="exist_$1+$2.tar.gz"
BUNGENI_APPS_HOME="/opt/bungeni/bungeni_apps"

echo "Zipping exist"
tar cvzf exist/$EXIST_ZIP_FILE /opt/bungeni --exclude=$BUNGENI_APPS_HOME/bungeni* --exclude=$BUNGENI_APPS_HOME/logs* --exclude=$BUNGENI_APPS_HOME/pid* --exclude=$BUNGENI_APPS_HOME/config/glue.ini --exclude=$BUNGENI_APPS_HOME/config/supervisord.conf --exclude=$BUNGENI_APPS_HOME/python* --exclude=/opt/bungeni/exec* --exclude=$BUNGENI_APPS_HOME/.* --exclude=/opt/bungeni/.* --exclude=$BUNGENI_APPS_HOME/rabbitmq*

cd exist && ./prepare_debpackfolder.sh $1+$2 $EXIST_ZIP_FILE $3
