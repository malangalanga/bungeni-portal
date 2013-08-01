#!/bin/bash
#===============================================================================
#
#          FILE:  prepare_debpackfolder.sh
#
#         USAGE:  ./prepare_debpackfolder.sh <release name> <pre-built-portal.tar.gz> <arch>
#
#   DESCRIPTION:  Generate portal control file and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh, ${PORTAL_REL_FOLDER}/run.sh
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
PORTAL_SIZE=$(getsize ../portal.include ../portal.exclude)

logger.printTask "[Portal] Setting up debian package..."
cp -R portal_version_revision $PORTAL_REL_FOLDER

logger.printTask "[Portal] Setting version control info."
sed -i "s/__PORTAL_VER__/${PORTAL_REL}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${PORTAL_ARCH}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${PORTAL_SIZE}/g" ./$PORTAL_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[Portal] Unzipping..."
printf "\n\n"
{
   tar xf $PORTAL_TAR --directory=./$PORTAL_REL_FOLDER/debian
   } >> /dev/null
   
logger.printTask "[Portal] Clean out development files.."
 rm -rf $PORTAL_REL_FOLDER/.svn $PORTAL_REL_FOLDER/debian/.svn || true
 find  $PORTAL_REL_FOLDER/debian/DEBIAN \( -name ".svn" \) -exec rm -rf {} \; || true
 find  $PORTAL_REL_FOLDER/debian/etc    \( -name ".svn" \) -exec rm -rf {} \; || true
 rm -rf $PORTAL_REL_FOLDER/debian/opt/.svn $PORTAL_REL_FOLDER/debian/opt/bungeni/.svn || true
 # remove .svn folders comment this out to build a dist package
 #find $BUNGENI_REL_FOLDER/debian/opt/bungeni/bungeni_apps -name ".svn" -exec rm -rf {} \; || true 
 find $PORTAL_REL_FOLDER \( -name "*.tmp" -or -name "*.pyc" -or -name "*.pyo" -or -name "*.log" \) -exec rm -rf {} \;

logger.printTask "[Portal] Now run will attempt to execute run.sh in the ${PORTAL_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   printf "\n\n"
   cd $PORTAL_REL_FOLDER && ./run.sh $PORTAL_ARCH
fi

mv $PORTAL_DEB ../../


