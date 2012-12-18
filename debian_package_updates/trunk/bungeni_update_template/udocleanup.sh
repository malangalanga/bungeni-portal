#!/bin/bash
#===============================================================================
#
#          FILE:  udoclean.sh
#
#         USAGE:  ./udoclean.sh
#
#   DESCRIPTION:  Does clean update previous and latest - ctrl and data folders,
#				  removes diff files 						
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Weru, samweru@gmail.com
#       COMPANY:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================

rm -rf previous/data
rm -rf previous/ctrl

rm -rf latest/data
rm -rf latest/ctrl

rm *.diff
