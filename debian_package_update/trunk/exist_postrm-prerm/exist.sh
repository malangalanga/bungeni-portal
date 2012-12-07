#!/bin/bash

. _bashtasklog.sh
. _debpackfunctions.sh

new bashtasklog logger

EXIST_PACKAGE_DATE=$(getdate)
EXIST_REL_FOLDER="bungeni-exist-db-update_2.1.0_17081-2_${EXIST_PACKAGE_DATE}"
EXIST_ARCH=$(getarchtype)
EXIST_SIZE=0

logger.printTask "[ExistDb] Setting up debian package folder."
cp -R exist-db_version_revision $EXIST_REL_FOLDER
rm -rf `find ./${EXIST_REL_FOLDER} -type d -name .svn`

logger.printTask "[ExistDb] Setting version in control file."
sed -i "s/__PACKAGE_NAME__/bungeni-exist-db-update/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__EXIST_VER__/2.1.0+17081-2-${EXIST_PACKAGE_DATE}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${EXIST_ARCH}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${EXIST_SIZE}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control

cd $EXIST_REL_FOLDER && ./run.sh $EXIST_ARCH


