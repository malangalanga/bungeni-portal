if [ $# -ne 1 ]
then
        echo 'usage : ./svnup_head.sh <folder/package name>'
        exit 99
fi
svn up -rHEAD $1
