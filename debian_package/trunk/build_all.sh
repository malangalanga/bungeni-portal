#!/bin/bash
#===============================================================================
#
#          FILE:  build_all.sh
#
#         USAGE:  sudo ./build_all.sh
#
#   DESCRIPTION:  Builds all bungeni debian packages (bungeni, postgresql, plone, portal, exist-db)
#				  gets initialization values from deb.ini file.
#
#  REQUIREMENTS:  Run as sudo user		
#
#       OPTIONS:  ---
#          BUGS:  ---
#         NOTES:  ---
#  DEPENDENCIES:  _bashtasklog.sh, _debpackfunctions.sh		
#
#       AUTHORS:  Ashok Hariharan <ashok@parliaments.info>
#				  Samuel Weru <samweru@gmail.com>
#
#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

. _bashtasklog.sh
. _debpackfunctions.sh

if [ ! -e "deb.ini" ] ; then
    echo "deb.ini file does not exist!"
    exit 65
fi

#global
BUNGENI_APPS_HOME=$(getini deb.ini global apps_home)

#release and version info
BUNGENI_VERSION=$(getini deb.ini bungeni version)
EXIST_RELEASE=$(getini deb.ini exist release)
POSTGRES_VERSION=$(getini deb.ini postgresql version)

#local dir info
BUNGENI_DIR=$(getini deb.ini bungeni dir)
EXIST_DIR=$(getini deb.ini exist dir)
PLONE_DIR=$(getini deb.ini plone dir)
PORTAL_DIR=$(getini deb.ini portal dir)
POSTGRES_DIR=$(getini deb.ini postgres dir)

if [ ! -d $BUNGENI_APPS_HOME ]; then
	echo "Bungeni does not exists"
	exit 65
fi 

CURR_DIR=`pwd`
CURR_TIMESTAMP=`gettimestamp`
export CURR_DEB_LOG="${CURR_DIR}/deb-${CURR_TIMESTAMP}.log"

new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG

logger.printTask "******************************************************************" 
logger.printTask "[Builder] Started..." 

	if [ ! -z $BUNGENI_VERSION ] ; then
		logger.printTask "[Bungeni] Start building.." 
		yes | ./bungeni.sh $BUNGENI_VERSION
		logger.printTask "[Bungeni] Finished." 
	else
		logger.printFail "[Bungeni][Exiting] Please set bungeni version in deb.ini file!"
	fi
logger.printTask "------------------------------------------------------------------" 
logger.printTask "[ExistDb] Building..." 
	if [ ! -d $EXIST_DIR ] ; then
		logger.printFail "[ExistDb][Exiting] ExistDB directory does not exist!"
	else
		if [ ! -z $EXIST_RELEASE ] ; then
			logger.printTask "[ExistDb] Started.." 
			yes | ./exist.sh $EXIST_RELEASE
			logger.printTask "[ExistDb] Finished." 
		else
			logger.printFail "[ExistDb][Exiting] Please set exist release in deb.ini file!"
		fi
	fi
logger.printTask "------------------------------------------------------------------" 
logger.printTask "[Portal] Building..." 
	if [ ! -d $PORTAL_DIR ] ; then
		logger.printFail "[Portal] directory does not exist!"
	else
		logger.printTask "[Portal] Started.." 
		yes | ./portal.sh
		logger.printTask "[Portal] Finished."
	fi
logger.printTask "------------------------------------------------------------------" 
logger.printTask "[Plone] Building..." 
	if [ ! -d $PLONE_DIR ] ; then
		logger.printFail "[Plone] directory does not exist!"
	else
		logger.printTask "[Plone] Started.." 
		yes | ./plone.sh
		logger.printTask "[Plone] Finished." 
	fi		
logger.printTask "------------------------------------------------------------------" 
logger.printTask "[PostgreSQL] Building..." 
	if [ ! -d $POSTGRES_DIR ] ; then
		logger.printFail "[PostgreSQL] directory does not exist!"
	else
		logger.printTask "[PostgreSQL] Started.." 
		yes | ./postgresql.sh $POSTGRES_VERSION
		logger.printTask "[PostgreSQL] Finished."
	fi
logger.printTask "[Builder] Finished." 
logger.printOk


