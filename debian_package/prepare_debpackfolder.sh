#!/bin/bash


#set -x verbose

EXPECTED_ARGS=2

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-bungeni.tar.gz>"
 exit 65
fi

BUNGENI_VER="1.0"
BUNGENI_REL="$BUNGENI_VER+$1"
BUNGENI_REL_FOLDER="bungeni_$BUNGENI_REL"
BUNGENI_TAR=$2
echo "found bungeni in $BUNGENI_TAR"

cp -R bungeni_version_revision $BUNGENI_REL_FOLDER

find ./$BUNGENI_REL_FOLDER -name '.svn' -print0 | xargs -0 rm -rf

echo "Setting version in control file"

sed -i "s/__BUNGENI_VER__/$BUNGENI_REL/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control

echo "Adding bungeni to debian package"

tar xvf $BUNGENI_TAR --directory=./$BUNGENI_REL_FOLDER/debian

echo "Now run will attempt to execute run.sh in the $BUNGENI_REL_FOLDER"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $BUNGENI_REL_FOLDER && ./run.sh
fi


