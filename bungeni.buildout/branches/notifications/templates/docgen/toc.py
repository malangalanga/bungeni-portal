import sys
"""
Searches and Replaces TABLE_OF_CONTENT placeholder with 
table of content generated in toc.txt within the generated
html pages
"""
ptoc = sys.argv[1]
phtml=sys.argv[2]
ftoc=open(ptoc)
stoc=ftoc.read()
fhtml=open(phtml)
shtml=fhtml.read()
snew=shtml.replace("TABLE_OF_CONTENT", stoc)
fhtml.close()
fhtml=open(phtml,"w")
fhtml.write(snew)
fhtml.close()



