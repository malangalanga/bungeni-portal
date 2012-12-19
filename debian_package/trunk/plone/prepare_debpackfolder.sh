#!/bin/bash
#===============================================================================
#
#          FILE:  prepare_debpackfolder.sh
#
#         USAGE:  ./prepare_debpackfolder.sh <release name> <pre-built-plone.tar.gz> <arch>
#
#   DESCRIPTION:  Generate plone control file and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh, ${PLONE_REL_FOLDER}/run.sh
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
   echo "Usage: `basename $0` <release name> <pre-built-plone.tar.gz> <arch>"
   exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
   new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
   new bashtasklog logger
fi

PLONE_RELEASE_NAME=(${1//+/ })
PLONE_VER="${PLONE_RELEASE_NAME[0]}"
PLONE_REL="$PLONE_VER+${PLONE_RELEASE_NAME[1]}"
PLONE_REL_FOLDER="bungeni-plone_${PLONE_REL}"
PLONE_TAR=$2
PLONE_ARCH=$3
PLONE_DEB="${PLONE_REL_FOLDER}_${PLONE_ARCH}.deb"
PLONE_SIZE=$(getsize ../plone.include ../plone.exclude)

logger.printTask "[Plone] Setting up debian package folder."
cp -R plone_version_revision $PLONE_REL_FOLDER

logger.printTask "[Plone] Setting version in control file."
sed -i "s/__PLONE_VER__/${PLONE_REL}/g" ./$PLONE_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${PLONE_ARCH}/g" ./$PLONE_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${PLONE_SIZE}/g" ./$PLONE_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[Plone] Unzipping..."
printf "\n\n"
{
   tar xf $PLONE_TAR --directory=./$PLONE_REL_FOLDER/debian
   } >> /dev/null
   
logger.printTask "[Plone] Clean out development files.."
printf "\n\n"
{
	find $PLONE_REL_FOLDER -name "*.svn" -exec rm -rf {} \;
	} > /dev/null 2>&1 

logger.printTask "[Plone] Now run will attempt to execute run.sh in the ${PLONE_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   printf "\n\n"
   cd $PLONE_REL_FOLDER && ./run.sh $PLONE_ARCH
fi

mv $PLONE_DEB ../../

