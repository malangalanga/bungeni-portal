#Generates the table of content
echo "<types>"
for f in $1/workspace/*.xml
do
   xpref=`basename $f .xml` ;
   if [ "$xpref" != "tabs" ];
   then
     xpref=`basename $f .xml` ;
     elem="<type>$xpref</type>" ;
     echo $elem ;
   fi
done
echo "</types>"
