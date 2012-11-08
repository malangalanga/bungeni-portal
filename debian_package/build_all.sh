#!/bin/bash

getini() 
{
	echo $(cat deb.ini | grep $1 | awk -F"=" '!/^($|#)/ {print $2}')	 	
}

BUILD_DATE=$(date +"%Y-%m-%d")
BUILD_STAMPDATETIME=$(date +"%Y%m%d-%H%M%S")

if [ ! -e "deb.ini" ] ; then
    echo "deb.ini file does not exist!"
    exit 65
fi

#release and version info
BUNGENI_VERSION=$(getini bungeni_version)
EXIST_RELEASE=$(getini exist_release)

#local dir info
BUNGENI_APPS_HOME=$(getini bungeni_apps_dir)
BUNGENI_DIR=$(getini bungeni_dir)
EXIST_DIR=$(getini exist_dir)
PLONE_DIR=$(getini plone_dir)
PORTAL_DIR=$(getini portal_dir)

if [ ! -d $BUNGENI_APPS_HOME ]; then
	echo "Bungeni does not exists"
	exit 65
fi 

{
	echo "-------------------------Building Bungeni ------------------------" 1>&2
		if [ ! -z $BUNGENI_VERSION ] ; then
			echo "[Bungeni $BUILD_DATE][$(date +%H:%M:%S)] BUNGENI_VERSION "$BUNGENI_VERSION	
			echo "[Bungeni $BUILD_DATE][$(date +%H:%M:%S)] Begun" >> deb.log
			yes | ./bungeni.sh $BUNGENI_VERSION
			echo "[Bungeni $BUILD_DATE][$(date +%H:%M:%S)] Finished" >> deb.log
		else
			echo "[Bungeni $BUILD_DATE][$(date +%H:%M:%S)][Exiting] Please set bungeni version in deb.ini file"
			echo "Please set bungeni version in deb.ini file" 1>&2
		fi
	echo "-------------------------Building Exist---------------------------" 1>&2
		if [ ! -d $EXIST_DIR ] ; then
			echo "[Exist $BUILD_DATE][$(date +%H:%M:%S)][Exiting] ExistDB directory does not exist"
			echo "ExistDB directory does not exist" 1>&2
		else
			if [ ! -z $EXIST_RELEASE ] ; then
				echo "[Exist $BUILD_DATE][$(date +%H:%M:%S)] Begun" >> deb.log
				yes | ./exist.sh $EXIST_RELEASE
				echo "[Exist $BUILD_DATE][$(date +%H:%M:%S)] Finished" >> deb.log
			else
				echo "[Exist $BUILD_DATE][$(date +%H:%M:%S)][Exiting] Please set exist release in deb.ini file"
				echo "Please set exist release in deb.ini file" 1>&2
			fi
		fi
	echo "-------------------------Building Portal -------------------------" 1>&2
		if [ ! -d $PORTAL_DIR ] ; then
			echo "[Portal $BUILD_DATE][$(date +%H:%M:%S)] Portal directory does not exist"
			echo "Portal directory does not exist" 1>&2
		else
			echo "[Portal $BUILD_DATE][$(date +%H:%M:%S)] Begun" >> deb.log
			yes | ./portal.sh
			echo "[Portal $BUILD_DATE][$(date +%H:%M:%S)] Finished" >> deb.log
		fi
	echo "-------------------------Building Plone---------------------------" 1>&2
		if [ ! -d $PLONE_DIR ] ; then
			echo "[Plone $BUILD_DATE][$(date +%H:%M:%S)] Plone directory does not exist"
			echo "Plone directory does not exist" 1>&2
		else
			echo "[Plone $BUILD_DATE][$(date +%H:%M:%S)] Begun" >> deb.log
			yes | ./plone.sh
			echo "[Plone $BUILD_DATE][$(date +%H:%M:%S)] Finished" >> deb.log
		fi		
	echo "------------------------Finished Building-------------------------" 1>&2

} >> deb.sh.$BUILD_STAMPDATETIME.log
