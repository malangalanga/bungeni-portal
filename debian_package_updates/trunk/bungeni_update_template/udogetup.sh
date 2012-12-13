#!/bin/bash

#set -v

. _bashtasklog.sh
. _debpackfunctions.sh

new bashtasklog logger

PACKAGE_NAME=$(getproperty update.ini package)
VERSION=$(getproperty update.ini version)
DEPENDS=$(getproperty update.ini dependencies)
HOME_PAGE=$(getproperty update.ini home)
DESCR=$(getproperty update.ini description)
DATE=$(getdate)
ARCH_TYPE=$(getarchtype)
RELEASE_NAME="${PACKAGE_NAME}_${VERSION}_${DATE}"
PACK_HOME=`pwd`/update
SIZE=0

ZIP_FILE="${RELEASE_NAME}.tar.gz"

logger.printTask "Setting up debian package folder."
cd $PACK_HOME
cp -R update_version_revision $RELEASE_NAME
rm -rf `find ./${RELEASE_NAME} -type d -name .svn`

logger.printTask "Zipping update files."
cat ../common.diff ../include.diff > $RELEASE_NAME.include
cd ../latest/data
tar -czf $PACK_HOME/$ZIP_FILE -T $PACK_HOME/$RELEASE_NAME.include
cd $PACK_HOME
tar xf $ZIP_FILE --directory=./$RELEASE_NAME/debian

logger.printTask "Creating control file."
sed -i "s/__PACKAGE_NAME__/${PACKAGE_NAME}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__ARCH__/${ARCH_TYPE}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__SIZE__/${SIZE}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__VERSION__/${VERSION}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__DEPENDS__/${DEPENDS}/g" ./$RELEASE_NAME/debian/DEBIAN/control

cd $RELEASE_NAME && ./run.sh $ARCHTYPE


