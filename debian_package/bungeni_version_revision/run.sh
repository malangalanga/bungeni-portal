dpkg-deb --build debian
CURDIR=`pwd`
mv debian.deb `basename $CURDIR`.deb
