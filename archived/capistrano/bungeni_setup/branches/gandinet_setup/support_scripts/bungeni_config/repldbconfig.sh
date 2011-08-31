# $1 = database name
# $2 = bungeni installation folder path without trailing backslas e.g./home/undesa/cap_installs/bungeni_install/bungeni/current
EXPECTED_ARGS=2
BAD_ARGS=99
if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: repldbconfig.sh <db name> <install folder path without trailing backslas>"
  exit $BAD_ARGS
fi

file_path="src/bungeni.portal/bungeni/portal"
file_name="configure.zcml"
full_path="$2/$file_path/$file_name"

rr="postgres://demodb.bungeni.org/$1"
echo $rr | sed  's/\:/\\\:/g' | sed 's/\//\\\//g' | sed 's/\./\\\./g' > out.txt
export FILE_DATA=( $( /bin/cat out.txt ) )
for I in $(/usr/bin/seq 0 $((${#FILE_DATA[@]} - 1)))
	do
		echo $I $FILE_DATA[$i]
	done
dname=`date +%Y%M%d-%s`
bakname="configure-$dname.zcml"

cp "$full_path" "$2/$file_path/$bakname"
rm out.txt 
sed -i 's/postgres\:\/\/localhost\/bungeni/'$FILE_DATA'/g' $full_path
cat $full_path | grep $1


