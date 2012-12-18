#!/bin/bash
#===============================================================================
#
#          FILE:  udoget.sh
#
#         USAGE:  ./udoget.sh
#
#   DESCRIPTION:  Generates update debian package	
#
#       OPTIONS:  ---
#  REQUIREMENTS:  previous and latest releases extracted using udoxtract.sh and
#				  udodiff.sh done to generate common.diff, include.diff and 
#   			  exclude.diff in that order
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Weru, samweru@gmail.com
#       COMPANY:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

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
RELEASE_NAME="${PACKAGE_NAME}-${VERSION}-${DATE}"
PACK_HOME=`pwd`/update
SIZE=0

ZIP_FILE="${RELEASE_NAME}.tar.gz"

logger.printTask "Setting up debian package folder."
cd $PACK_HOME
cp -R update_version_revision $RELEASE_NAME
cp ../common.diff $PACK_HOME/$RELEASE_NAME/debian/opt/bungeni/updates/latest/common.list
cp ../exclude.diff $PACK_HOME/$RELEASE_NAME/debian/opt/bungeni/updates/latest/exclude.list
cp ../include.diff $PACK_HOME/$RELEASE_NAME/debian/opt/bungeni/updates/latest/include.list

rm -rf `find ./${RELEASE_NAME} -type d -name .svn`

logger.printTask "Zipping update files."
cat ../common.diff ../include.diff > $RELEASE_NAME.include
sed -i "s|/opt/|../latest/data/opt/|g" $RELEASE_NAME.include
#cd ../latest/data
tar --transform 's,latest/data/opt/,opt/,' -czf $ZIP_FILE -T $RELEASE_NAME.include

mv $ZIP_FILE $RELEASE_NAME/debian/opt/bungeni/updates/latest

logger.printTask "Creating control file."
sed -i "s/__PACKAGE_NAME__/${RELEASE_NAME}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__ARCH__/${ARCH_TYPE}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__SIZE__/${SIZE}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__VERSION__/${VERSION}-${DATE}/g" ./$RELEASE_NAME/debian/DEBIAN/control
sed -i "s/__DEPENDS__/${DEPENDS}/g" ./$RELEASE_NAME/debian/DEBIAN/control

cd $RELEASE_NAME && ./run.sh $ARCH_TYPE


