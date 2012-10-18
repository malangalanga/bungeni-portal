#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-bungeni.tar.gz> <arch>"
 exit 65
fi

echo "reading bungeni dependencies"
BUNGENI_DEPENDS=$(cat /opt/bungeni/exec/distro.ini | awk -v "RS=\n\n" -F "=" '/12.04/ {print $2}' | sed 's/#.*//' | tr -d '\n' | tr -s ' ' ', ' | sed 's/^.//')

BUNGENI_RELVER=(${1//+/ })
BUNGENI_VER="${BUNGENI_RELVER[0]}"
BUNGENI_REL="$BUNGENI_VER+${BUNGENI_RELVER[1]}"
BUNGENI_REL_FOLDER="bungeni_$BUNGENI_REL"
BUNGENI_TAR=$2
BUNGENI_ARCH=$3
BUNGENI_DEB="${BUNGENI_REL_FOLDER}_${3}.deb"

echo "found bungeni in $BUNGENI_TAR"

cp -R bungeni_version_revision $BUNGENI_REL_FOLDER

find ./$BUNGENI_REL_FOLDER -name '.svn' -print0 | xargs -0 rm -rf

echo "Setting version in control file"

sed -i "s/__BUNGENI_VER__/$BUNGENI_REL/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/$BUNGENI_ARCH/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__DEPENDS__/$BUNGENI_DEPENDS/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control

echo "Adding bungeni to debian package"

tar xvf $BUNGENI_TAR --directory=./$BUNGENI_REL_FOLDER/debian

echo "Now run will attempt to execute run.sh in the $BUNGENI_REL_FOLDER"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $BUNGENI_REL_FOLDER && ./run.sh $BUNGENI_ARCH
fi

mv $BUNGENI_DEB ../../

