#!/bin/bash
#===============================================================================
#
#          FILE:  udoxtract.sh
#
#         USAGE:  ./udoxtract.sh
#
#   DESCRIPTION:  Extracts latest and previous debian packages into ctrl and
#                 data folders
#
#       OPTIONS:  ---
#  REQUIREMENTS:  Place latest and previous debian package releases in thier 
# 				  respective folders
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Weru, samweru@gmail.com
#       COMPANY:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

mkdir -p previous/ctrl
mkdir -p latest/ctrl

mkdir -p previous/data
mkdir -p latest/data

ar p previous/*.deb control.tar.gz | tar zx --directory=previous/ctrl
ar p latest/*.deb control.tar.gz | tar zx --directory=latest/ctrl

ar p previous/*.deb data.tar.gz | tar vzx --directory=previous/data/ > previous/ctrl/list
ar p latest/*.deb data.tar.gz | tar vzx -X latest.exclude --directory=latest/data/ > latest/ctrl/list

sed -i 's/\.\//\//g' previous/ctrl/list
sed -i 's/\.\//\//g' latest/ctrl/list
