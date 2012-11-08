#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-portal.tar.gz> <arch>"
 exit 65
fi

PORTAL_RELVER=(${1//+/ })
PORTAL_VER="${PORTAL_RELVER[0]}"
PORTAL_REL="$PORTAL_VER+${PORTAL_RELVER[1]}"
PORTAL_REL_FOLDER="bungeni-portal_$PORTAL_REL"
PORTAL_TAR=$2
PORTAL_ARCH=$3
PORTAL_DEB="${PORTAL_REL_FOLDER}_${3}.deb"

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Setting up debian package..."
cp -R portal_version_revision $PORTAL_REL_FOLDER
find ./$PORTAL_REL_FOLDER/ -name '.svn' -print0 | xargs -0 rm -rf 

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Setting version control info."
sed -i "s/__PORTAL_VER__/$PORTAL_REL/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/$PORTAL_ARCH/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Extracting to debian package folder..."
tar xf $PORTAL_TAR --directory=./$PORTAL_REL_FOLDER/debian

echo "[Portal $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Now run will attempt to execute run.sh in the $PORTAL_REL_FOLDER"
read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $PORTAL_REL_FOLDER && ./run.sh $PORTAL_ARCH
fi

mv $PORTAL_DEB ../../


