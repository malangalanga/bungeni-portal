#! /bin/bash -e
#===============================================================================
#
#          FILE:  run.sh
#
#         USAGE:  ./run.sh <archtype>
#
#   DESCRIPTION:  Generate portal md5 hashes and debian package 
#
#          BUGS:  ---
#         NOTES:  ---
#
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh
#       AUTHORS:  Ashok Hariharan <ashok@parliaments.info>
#                 Samuel Weru <samweru@gmail.com>  
#
#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

. ../../_bashtasklog.sh
. ../../_debpackfunctions.sh

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[Portal] Generating md5sums..."
{
	printf "\n"
	
	cd ./debian && find .  -type f -not -path "*.svn*"  | grep -v 'DEBIAN'  | xargs md5sum > ../md5sums
	} &>> $CURR_DEB_LOG
	
cd ..
sed -i 's|./opt|opt|g' md5sums
mv md5sums debian/DEBIAN

logger.printTask "[Portal] Building Debian Package..."
{
	printf "\n\n"
	
	dpkg-deb --build debian 
	} &>> $CURR_DEB_LOG
	
CURDIR=`pwd`
mv debian.deb `basename $CURDIR`_$1.deb
