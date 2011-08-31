wget ftp://ftp.cs.tu-berlin.de/pub/misc/postgresql/v8.3.4/postgresql-8.3.4.tar.bz2
tar xvf postgresql-8.3.4.tar.bz2
cd postgresql-8.3.4
./configure --prefix=/home/undesa/disk1/postgres --enable-thread-safety --with-readline
make && make install
/home/undesa/disk1/postgres/bin/initdb -D /home/undesa/disk1/postgres-data
/home/undesa/disk1/postgres/bin/createdb angola
/home/undesa/disk1/postgres/bin/createdb kenya 
/home/undesa/disk1/postgres/bin/createdb uganda
/home/undesa/disk1/postgres/bin/createdb tanzania
/home/undesa/disk1/postgres/bin/createdb ghana   
/home/undesa/disk1/postgres/bin/createdb cameroon
/home/undesa/disk1/postgres/bin/createdb haiti   
/home/undesa/disk1/postgres/bin/createdb nigeria
/home/undesa/disk1/postgres/bin/createdb southafrica
/home/undesa/disk1/postgres/bin/createdb pap        
/home/undesa/disk1/postgres/bin/createdb mozambique
/home/undesa/disk1/postgres/bin/createdb mauritius
/home/undesa/disk1/postgres/bin/createdb rwanda

