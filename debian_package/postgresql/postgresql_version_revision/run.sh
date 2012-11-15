
. ../../_bashtasklog.sh
. ../../_debpackfunctions.sh

if [ ! -z $CURR_DEB_LOG ] ; then
	new bashtasklog logger -t -w 50 -l $CURR_DEB_LOG
else
	new bashtasklog logger
	CURR_DEB_LOG=/dev/null
fi

logger.printTask "[PostgreSQL] Generating md5sums..."
{
	printf "\n"
	
	cd ./debian && find .  -type f -not -path "*.svn*"  | grep -v 'DEBIAN'  | xargs md5sum > ../md5sums
	} &>> $CURR_DEB_LOG
	
cd ..
sed -i 's|./opt|opt|g' md5sums
mv md5sums debian/DEBIAN

logger.printTask "[PostgreSQL] Building Debian Package..."
{
	printf "\n\n"
	
	dpkg-deb --build debian 
	} &>> $CURR_DEB_LOG
	
CURDIR=`pwd`
mv debian.deb `basename $CURDIR`_$1.deb
