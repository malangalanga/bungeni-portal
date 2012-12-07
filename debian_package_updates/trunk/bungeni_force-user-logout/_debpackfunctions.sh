#!/bin/bash

#<ini_file> <ini_section> <ini_key>
getini(){	
	
	echo $(cat $1 | awk -v "RS=\n\n" '/\['$2'\]/ {print $0}' | grep $3 | awk -F"=" '!/^($|#)/ {print $2}'|tr -d '\r|[:space:]')
}

#<ini_file> <ini_key>
getproperty(){

	echo $(cat $1 | grep -w $2 | awk -F "=" '{print $2}' | tr -d '\t|[:space:]')
}

getdate(){
		
	echo $(date +"%Y-%m-%d")	
}

gettime(){
		
	echo $(date +%H:%M:%S)	
}

gettimestamp(){
	
	echo $(date +"%Y-%m-%d_%H%M%S")	
}

getrevinfo(){
	
	echo $(svn info $1 |grep Revision: |cut -c11-)
}

getarchtype(){
	
	if [ $(getconf LONG_BIT) == 64 ]
	then
		echo "amd64"
	else
		echo "i386"
	fi
}

getosver(){

	echo $(lsb_release -a | grep Release: | cut -c9- | tr -d "[:space:]")	
}

#<distro_ini>
getbungenideps(){
	
	echo $(cat $1 | awk -v "RS=\n\n" -F "=" '/'$(getosver)'/ {print $2}' | sed 's/#.*//' | tr -d '\n' | tr -s ' ' ', ' | sed 's/^.//')
}

#<include> <exclude>
getsize(){

	echo $(du -sc $(tr '\n' ' ' < $1) -X $2 | tail -1 | awk -F " " '{print $1}')	
}
