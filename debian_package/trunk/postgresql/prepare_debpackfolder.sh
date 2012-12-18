#!/bin/bash
#===============================================================================
#
#          FILE:  prepare_debpackfolder.sh
#
#         USAGE:  ./prepare_debpackfolder.sh <release name> <pre-built-postgres.tar.gz> <arch>
#
#   DESCRIPTION:  Generate postgresql control file and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh, ${POSTGRESQL_REL_FOLDER}/run.sh
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

#set -x

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <release name> <pre-built-postgres.tar.gz> <arch>"
 exit 65
fi

if [ ! -z $CURR_DEB_LOG ] ; then
   new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
   new bashtasklog logger
fi

POSTGRES_RELEASE_NAME=(${1//+/ })
POSTGRES_VER="${POSTGRES_RELEASE_NAME[0]}"
POSTGRES_REL="$POSTGRES_VER+${POSTGRES_RELEASE_NAME[1]}"
POSTGRES_REL_FOLDER="bungeni-postgresql_${POSTGRES_REL}"
POSTGRES_TAR=$2
POSTGRES_ARCH=$3
POSTGRES_DEB="${POSTGRES_REL_FOLDER}_${POSTGRES_ARCH}.deb"
POSTGRES_SIZE=$(getsize ../postgresql.include ../postgresql.exclude)

logger.printTask "[PostgreSQL] Setting up debian package..."
cp -R postgresql_version_revision $POSTGRES_REL_FOLDER
find ./$POSTGRES_REL_FOLDER/ -name '.svn' -print0 | xargs -0 rm -rf 

logger.printTask "[PostgreSQL] Setting version control info."
sed -i "s/__POSTGRES_VER__/${POSTGRES_REL}/g" ./$POSTGRES_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__ARCH__/${POSTGRES_ARCH}/g" ./$POSTGRES_REL_FOLDER/debian/DEBIAN/control
sed -i "s/__SIZE__/${POSTGRES_SIZE}/g" ./$POSTGRES_REL_FOLDER/debian/DEBIAN/control

logger.printTask "[PostgreSQL] Unzipping..."
printf "\n\n"
{
   tar xf $POSTGRES_TAR --directory=./$POSTGRES_REL_FOLDER/debian
   } >> /dev/null

logger.printTask "[PostgreSQL] Now run will attempt to execute run.sh in the ${POSTGRES_REL_FOLDER}"
printf "\n"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   printf "\n\n"
   cd $POSTGRES_REL_FOLDER && ./run.sh $POSTGRES_ARCH
fi

mv $POSTGRES_DEB ../../
