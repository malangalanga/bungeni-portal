#!/bin/bash
#===============================================================================
#
#          FILE:  prepare_debpackfolder.sh
#
#         USAGE:  ./prepare_debpackfolder.sh <release name> <pre-built-bungeni.tar.gz> <arch>
#
#   DESCRIPTION:  Generate bungeni control file and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh, ${BUNGENI_REL_FOLDER}/run.sh
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
 echo "Usage: `basename $0` <release name> <pre-built-bungeni.tar.gz> <arch>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
fi


logger.printTask "[Bungeni] Reading bungeni dependencies info..."
printf "\n\n"

BUNGENI_OTHER_DEPENDS="fabric"
BUNGENI_DISTRO_INI=$(getini ../deb.ini global ini)
BUNGENI_DEPENDS=$(getbungenideps ${BUNGENI_DISTRO_INI})

BUNGENI_RELEASE_NAME=(${1//+/ })
BUNGENI_VER="${BUNGENI_RELEASE_NAME[0]}"
BUNGENI_REL="${BUNGENI_VER}+${BUNGENI_RELEASE_NAME[1]}"
BUNGENI_REL_FOLDER="bungeni_${BUNGENI_REL}"
BUNGENI_TAR=$2
BUNGENI_ARCH=$3
BUNGENI_DEB="${BUNGENI_REL_FOLDER}_${BUNGENI_ARCH}.deb"
BUNGENI_SIZE=$(getsize ../bungeni.include ../bungeni.exclude)

logger.printTask "[Bungeni] Setting debian package folder."
cp -R bungeni_version_revision $BUNGENI_REL_FOLDER

logger.printTask "[Bungeni] Setting verion in control file."
sed -i "s/__BUNGENI_VER__/${BUNGENI_REL}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${BUNGENI_ARCH}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__DEPENDS__/${BUNGENI_OTHER_DEPENDS},${BUNGENI_DEPENDS}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${BUNGENI_SIZE}/g" ./$BUNGENI_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[Bungeni] Unzipping..."
printf "\n\n"
{
	tar xf $BUNGENI_TAR --directory=./$BUNGENI_REL_FOLDER/debian
	} >> /dev/null
	
logger.printTask "[Bungeni] Clean out development files.."
printf "\n\n"
{
	find $BUNGENI_REL_FOLDER \( -name "*.svn" -or -name "*.tmp" -or -name "*.pyc" -or -name "*.pyo" -or -name "*.log" \) -exec rm -rf {} \;
	} > /dev/null 2>&1 

logger.printTask "[Bungeni] Now run will attempt to execute run.sh in the ${BUNGENI_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
	printf "\n\n"
	cd $BUNGENI_REL_FOLDER && ./run.sh $BUNGENI_ARCH
fi

mv $BUNGENI_DEB ../../

