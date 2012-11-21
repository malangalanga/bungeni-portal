#!/bin/bash

. ../_bashtasklog.sh
. ../_debpackfunctions.sh

#set -x verbose

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-exist.tar.gz> <arch>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
fi

EXIST_RELASE_NAME=(${1//+/ })
EXIST_VER="${EXIST_RELASE_NAME[0]}"
EXIST_REL="${EXIST_VER}+${EXIST_RELASE_NAME[1]}"
EXIST_REL_FOLDER="bungeni-exist-db_${EXIST_REL}"
EXIST_TAR=$2
EXIST_ARCH=$3
EXIST_DEB="${EXIST_REL_FOLDER}_${EXIST_ARCH}.deb"
EXIST_SIZE=$(getsize ../exist.include ../exist.exclude)

logger.printTask "[ExistDb] Setting up debian package folder."
cp -R exist-db_version_revision $EXIST_REL_FOLDER
rm -rf `find ./${EXIST_REL_FOLDER} -type d -name .svn`

logger.printTask "[ExistDb] Setting version in control file."
sed -i "s/__EXIST_VER__/${EXIST_REL}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${EXIST_ARCH}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${EXIST_SIZE}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[ExistDb] Unzipping..."
printf "\n\n"
{
	tar xf $EXIST_TAR --directory=./$EXIST_REL_FOLDER/debian
	} >> /dev/null

logger.printTask "[ExistDb] Now run will attempt to execute run.sh in the ${EXIST_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
	printf "\n\n"
	cd $EXIST_REL_FOLDER && ./run.sh $EXIST_ARCH
fi

mv $EXIST_DEB ../../


