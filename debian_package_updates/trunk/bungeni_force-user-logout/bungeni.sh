#!/bin/bash

set -v

. _bashtasklog.sh
. _debpackfunctions.sh

new bashtasklog logger

BUNGENI_PACKAGE_DATE=$(getdate)
BUNGENI_REL_FOLDER="bungeni-update_1.0_${BUNGENI_PACKAGE_DATE}"
BUNGENI_ARCH=$(getarchtype)
BUNGENI_SIZE=0

logger.printTask "[Bungeni] Setting up debian package folder."
cp -R bungeni_version_revision $BUNGENI_REL_FOLDER
rm -rf `find ./${BUNGENI_REL_FOLDER} -type d -name .svn`

logger.printTask "[Bungeni] Setting version in control file."
sed -i "s/__PACKAGE_NAME__/bungeni-update/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__BUNGENI_VER__/1.0-${BUNGENI_PACKAGE_DATE}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${BUNGENI_ARCH}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${BUNGENI_SIZE}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control

cd $BUNGENI_REL_FOLDER && ./run.sh $BUNGENI_ARCH


