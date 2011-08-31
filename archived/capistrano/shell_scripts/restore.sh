if [ $# -ne 1 ]
then
	echo 'usage : ./restore.sh <backup name>'
	exit 99
fi
cd ~/cap_installs/bungeni_install/bungeni/current && ./parts/postgresql/bin/dropdb bungeni
cd ~/cap_installs/bungeni_install/bungeni/current && ./parts/postgresql/bin/createdb bungeni
echo restoring $1
cd ~/cap_installs/bungeni_install/bungeni/current && ./parts/postgresql/bin/psql bungeni < bak_$1
cd
echo restored $1
