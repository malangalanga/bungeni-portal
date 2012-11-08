#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-plone.tar.gz> <arch>"
 exit 65
fi

PLONE_RELVER=(${1//+/ })
PLONE_VER="${PLONE_RELVER[0]}"
PLONE_REL="$PLONE_VER+${PLONE_RELVER[1]}"
PLONE_REL_FOLDER="bungeni-plone_$PLONE_REL"
PLONE_TAR=$2
PLONE_ARCH=$3
PLONE_DEB="${PLONE_REL_FOLDER}_${3}.deb"

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Setting up debian package folder."
cp -R plone_version_revision $PLONE_REL_FOLDER
find ./$PLONE_REL_FOLDER -name '.svn' -print0 | xargs -0 rm -rf

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Setting version in control file."
sed -i "s/__PLONE_VER__/$PLONE_REL/g" ./$PLONE_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/$PLONE_ARCH/g" ./$PLONE_REL_FOLDER/debian/DEBIAN/control

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Extracting to debian package folder..."
tar xf $PLONE_TAR --directory=./$PLONE_REL_FOLDER/debian

echo "[Plone $(date +%Y-%m-%d)][$(date +%H:%M:%S)] Now run will attempt to execute run.sh in the $PLONE_REL_FOLDER"
read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $PLONE_REL_FOLDER && ./run.sh $PLONE_ARCH
fi


mv $PLONE_DEB ../../

