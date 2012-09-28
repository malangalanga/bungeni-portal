#!/bin/bash

die () {
    echo >&2 "$@"
    exit 1
}

set -x verbose

[ "$#" -eq 2 ] || die "2 parameters required : 1 release name argument required and 1 path to a bungeni pre-built tar.gz archive , $# provided"


BUNGENI_REL="bungeni_1.0+$1"
BUNGENI_TAR=$2

cp -R bungeni_version_revision $BUNGENI_REL

find ./$BUNGENI_REL -name '.svn' -print0 | xargs rm -rf

tar xvf $BUNGENI_TAR --directory=./$BUNGENI_REL/debian

echo "Now run will attempt to execute run.sh in the $BUNGENI_REL"

read -p "Are you sure (Yy) ? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
   cd $BUNGENI_REL && ./run.sh
fi


