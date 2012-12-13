. ../../_bashtasklog.sh
. ../../_debpackfunctions.sh

new bashtasklog logger

logger.printTask "Generating md5sums..."	
cd ./debian && find .  -type f -not -path "*.svn*"  | grep -v 'DEBIAN'  | xargs md5sum > ../md5sums
	
cd ..
sed -i 's|./opt|opt|g' md5sums
mv md5sums debian/DEBIAN

logger.printTask "Building Debian Package..."
printf "\n\n"
dpkg-deb --build debian 
	
CURDIR=`pwd`
mv debian.deb `basename $CURDIR`_$1.deb
mv `basename $CURDIR`_$1.deb ../../
