#!/bin/bash
#
# get parameters from ini
# gather files in gz file 
# create debian package
#
#
source ../../_bashtasklog.sh
source ../../_debpackfunctions.sh

EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ] 
then
 echo "Usage: `basename $0` <version>"
 exit 65
fi

UPDATE_VERSION=$(getini update.ini update version)
UPDATE_DEPENDS=$(getini update.ini update depends)
#UPDATE_BUILD_DATE=$(getdate)
#OS_ARCH_TYPE=$(getarchtype)

echo $UPDATE_VERSION
echo $UPDATE_DEPENDS
#print $UPDATE_BUILD_DATE
#print $OS_ARCH_TYPE
