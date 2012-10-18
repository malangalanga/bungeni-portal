#!/bin/bash


#set -x verbose

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-exist.tar.gz> <arch>"
 exit 65
fi

EXIST_RELVER=(${1//+/ })
EXIST_VER="${EXIST_RELVER[0]}"
EXIST_REL="$EXIST_VER+${EXIST_RELVER[1]}"
EXIST_REL_FOLDER="bungeni-exist-db_$EXIST_REL"
EXIST_TAR=$2
EXIST_ARCH=$3
EXIST_DEB="${EXIST_REL_FOLDER}_${3}.deb"

echo "found exist in $EXIST_TAR"

cp -R exist-db_version_revision $EXIST_REL_FOLDER

#find ./$EXIST_REL_FOLDER -name '.svn' -print0 | xargs -0 rm -rf
rm -rf `find ./$EXIST_REL_FOLDER -type d -name .svn`

echo "Setting version in control file"

sed -i "s/__EXIST_VER__/$EXIST_REL/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/$EXIST_ARCH/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control

echo "Adding exist to debian package"

tar xvf $EXIST_TAR --directory=./$EXIST_REL_FOLDER/debian

echo "Now run will attempt to execute run.sh in the $EXIST_REL_FOLDER"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $EXIST_REL_FOLDER && ./run.sh $EXIST_ARCH
fi

mv $EXIST_DEB ../../


