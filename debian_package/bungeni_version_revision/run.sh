echo "Generating md5sums"
cd ./debian && find .  -type f -not -path "*.svn*"  | grep -v 'DEBIAN'  | xargs md5sum > ../md5sums
cd ..
sed -i 's|./opt|opt|g' md5sums
mv md5sums debian/DEBIAN
echo "Building Debian Package"
dpkg-deb --build debian
CURDIR=`pwd`
mv debian.deb `basename $CURDIR`_$1.deb
