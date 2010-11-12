#Generates the table of content
echo "<ul id=\"menu\">"
for f in /home/undesa/cinst/bungeni/src/bungeni.main/bungeni/core/workflows/*.xml
do 
        xpref=`basename $f .xml`
            html=$xpref.html
                echo "<li><a href=\""$html"\">$xpref</a></li>"
            done
            echo "</ul>"
