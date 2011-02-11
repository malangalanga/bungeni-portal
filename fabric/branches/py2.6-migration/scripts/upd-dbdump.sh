#!/bin/bash
#This script updates db dumps from a bungnei db for use on a different computer
#It updates the owner of the db dump with a new user owner
#input file , $2 = output file , $3 = input user , $4 = output user
EXPECTED_ARGS=4
BAD_ARGS=99
if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: upd-dbdump.sh <input-file> <output-file> <input-user> <output-user>"
  exit $BAD_ARGS
fi
sed 's/Owner\: '$3'/Owner\: '$4'/g' $1  |  sed 's/FROM '$3'\;/FROM '$4'\;/g' | sed 's/TO '$3'\;/TO '$4'\;/g' > $2
