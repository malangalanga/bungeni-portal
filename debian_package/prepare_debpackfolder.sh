#!/bin/bash


#set -x verbose

EXPECTED_ARGS=2

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-bungeni.tar.gz>"
 exit 65
fi

BUNGENI_REL="bungeni_1.0+$1"
BUNGENI_TAR=$2
echo "found bungeni in $BUNGENI_TAR"

cp -R bungeni_version_revision $BUNGENI_REL

find ./$BUNGENI_REL -name '.svn' -print0 | xargs -0 rm -rf

tar xvf $BUNGENI_TAR --directory=./$BUNGENI_REL/debian

echo "Now run will attempt to execute run.sh in the $BUNGENI_REL"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $BUNGENI_REL && ./run.sh
fi


