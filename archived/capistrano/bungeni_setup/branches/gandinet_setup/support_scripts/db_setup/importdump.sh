cd /home/undesa/disk1
wget http://deploydb.bungeni.org/pg/onlinedmp.tar.gz
tar xvf onlinedmp.tar.gz
/home/undesa/disk1/postgres/bin/psql angola < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql kenya  < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql uganda < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql tanzania < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql ghana    < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql cameroon < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql haiti    < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql nigeria < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql southafrica < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql pap         < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql mozambique < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql mauritius < onlinedmp.txt
/home/undesa/disk1/postgres/bin/psql rwanda < onlinedmp.txt

