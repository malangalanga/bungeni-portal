#!/bin/bash
#===============================================================================
#
#          FILE:  udodiff.sh
#
#         USAGE:  ./udodiff.sh
#
#   DESCRIPTION:  Does diff of previous and latest folders and generates list of
#				  files that are common, files that are excluded from previous
#				  release and files included in latest release 	
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

#diff
diff -rq previous/data/ latest/data | grep -vf filter.words | grep "^Files.*differ$" | sed 's/^Files \(.*\) and .* differ$/\1/' | cut -b -13 --complement > common.diff

#only in previous
diff -rq previous/data/ latest/data | grep -vf filter.words | grep "Only in previous" | sed 's/Only in //g' | sed 's/: /\//g' | cut -b -13 --complement > exclude.diff

#only in latest
diff -rq previous/data/ latest/data | grep -vf filter.words | grep "Only in latest" | sed 's/Only in //g' | sed 's/: /\//g' | cut -b -11 --complement > include.diff

