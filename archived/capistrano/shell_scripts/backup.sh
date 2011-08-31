if [ $# -ne 1 ] 
then
	echo 'usage : ./backup.sh <backup name>'
	exit 99
fi
cd ~/cap_installs/bungeni_install/bungeni/current && ./parts/postgresql/bin/pg_dump bungeni > bak_$1
cd
echo backed up to  $1
