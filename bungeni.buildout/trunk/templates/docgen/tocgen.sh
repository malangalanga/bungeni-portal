#Generates the table of content
echo "<ul id=\"menu\">"
for f in $1/workflows/*.xml
do 
        xpref=`basename $f .xml`
            html=wf_$xpref.html
                echo "<li><a href=\""$html"\">$xpref</a></li>"
            done
            echo "</ul>"
