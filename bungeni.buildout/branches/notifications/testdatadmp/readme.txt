TEST DATA
---------
This folder contains the minimum data and sample data for a Bungeni installation 

Minimum Data
------------
min-dump.txt contains the minimum data required to start using a bungeni 
installation eg. country names, venues, etc. 

To install this data to an empty database do
./bin/psql -d bungeni < testdatadmp/min-dump.txt

Sample Data
-----------
dump.txt contains sample data generated using selenium scripts.

To install this data to an empty database do
./bin/psql -d bungeni < testdatadump/dump.txt


Different DB user
-----------------
Past data dumps had commands to set ownership of objects to match the original 
database. Current data dumps do not, so this step is not necessary but is
left here for reference.

The upd-dbdump.sh is used to update the data owner in the db dump file.

The default db dump owner is a user called "undesa", to use it in a different 
user context, use the script to generate a new dump from the undesa dump.

Usage: upd-dbdump.sh <input-file> <output-file> <input-user> <output-user>
