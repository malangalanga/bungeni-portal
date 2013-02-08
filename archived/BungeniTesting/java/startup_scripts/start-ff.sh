echo 'Starting Firefox'
export DISPLAY=:99
firefox_path=`cat firefox.path`
echo 'Running firefox at $firefox_path'
`echo $firefox_path` &
echo 'Started firefox'

