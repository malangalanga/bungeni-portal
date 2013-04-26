#!/bin/bash

############################
# Back Up Exist DB Framework
############################

echo "Please wait ..."
mkdir -p /opt/bungeni/updates/latest
chown -R bungeni:bungeni /opt/bungeni/updates/latest
su bungeni -l -c "JAVA_HOME=$JAVA_HOME \
		java -jar -Dexist.home=/opt/bungeni/bungeni_apps/exist  \
		/opt/bungeni/bungeni_apps/exist/start.jar backup -b /db/apps/framework -d /opt/bungeni/updates/latest \
		-ouri=xmldb:exist://127.0.0.1:8088/exist/xmlrpc"

tar -czf exist_fw.tar.gz /opt/bungeni/updates/latest/db
chown undesa:undesa exist_fw.tar.gz
rm -rf /opt/bungeni/updates/latest
echo "Done."
