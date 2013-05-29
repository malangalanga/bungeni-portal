#!/bin/bash
#===============================================================================
#
#          FILE:  prepare_debpackfolder.sh
#
#         USAGE:  ./prepare_debpackfolder.sh <release name> <pre-built-exist.tar.gz> <arch>
#
#   DESCRIPTION:  Generate exist-db control file and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh, ${EXIST_REL_FOLDER}/run.sh
#       AUTHORS:  Ashok Hariharan <ashok@parliaments.info>
#                 Samuel Weru <samweru@gmail.com>  
#
#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

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

logger.printTask "[ExistDb] Setting version in control file."
sed -i "s/__EXIST_VER__/${EXIST_REL}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${EXIST_ARCH}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${EXIST_SIZE}/g" ./$EXIST_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[ExistDb] Unzipping..."
printf "\n\n"
{
	tar xf $EXIST_TAR --directory=./$EXIST_REL_FOLDER/debian
	} >> /dev/null
	
logger.printTask "[ExistDb] Clean out development files.."
printf "\n\n"
rm -rf $EXIST_REL_FOLDER/.svn $EXIST_REL_FOLDER/debian/.svn  || true
find  $EXIST_REL_FOLDER/debian/DEBIAN \( -name ".svn" \) -exec rm -rf {} \; || true
find  $EXIST_REL_FOLDER/debian/etc    \( -name ".svn" \) -exec rm -rf {} \; || true
rm -rf $EXIST_REL_FOLDER/debian/opt/.svn $BUNGENI_REL_FOLDER/debian/opt/bungeni/.svn || true
find $EXIST_REL_FOLDER/debian/opt/bungeni/bungeni_apps/exist \( -name "*.svn" -or -name "*.tmp" -or -name "*.lock" -or -name "*.lck" -or -name "*.log" \) -exec rm -rf {} \;
find $EXIST_REL_FOLDER/debian/opt/bungeni/bungeni_apps/glue \( -name "*.tmp" -or -name "*.lock" -or -name "*.lck" -or -name "*.log" \) -exec rm -rf {} \;
logger.printTask "[ExistDb] Now run will attempt to execute run.sh in the ${EXIST_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
	printf "\n\n"
	cd $EXIST_REL_FOLDER && ./run.sh $EXIST_ARCH
fi

mv $EXIST_DEB ../../


