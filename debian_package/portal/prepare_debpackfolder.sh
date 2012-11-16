#!/bin/bash

. ../_bashtasklog.sh
. ../_debpackfunctions.sh

#set -x verbose

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-portal.tar.gz> <arch>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
   new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
   new bashtasklog logger
fi

PORTAL_RELEASE_NAME=(${1//+/ })
PORTAL_VER="${PORTAL_RELEASE_NAME[0]}"
PORTAL_REL="$PORTAL_VER+${PORTAL_RELEASE_NAME[1]}"
PORTAL_REL_FOLDER="bungeni-portal_${PORTAL_REL}"
PORTAL_TAR=$2
PORTAL_ARCH=$3
PORTAL_DEB="${PORTAL_REL_FOLDER}_${PORTAL_ARCH}.deb"
PORTAL_SIZE=$(getsize ../portal.exclude ../portal.include)

logger.printTask "[Portal] Setting up debian package..."
cp -R portal_version_revision $PORTAL_REL_FOLDER
find ./$PORTAL_REL_FOLDER/ -name '.svn' -print0 | xargs -0 rm -rf 

logger.printTask "[Portal] Setting version control info."
sed -i "s/__PORTAL_VER__/${PORTAL_REL}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${PORTAL_ARCH}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${PORTAL_SIZE}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[Portal] Unzipping..."
printf "\n\n"
{
   tar xf $PORTAL_TAR --directory=./$PORTAL_REL_FOLDER/debian
   } >> /dev/null

logger.printTask "[Portal] Now run will attempt to execute run.sh in the ${PORTAL_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   printf "\n\n"
   cd $PORTAL_REL_FOLDER && ./run.sh $PORTAL_ARCH
fi

mv $PORTAL_DEB ../../


