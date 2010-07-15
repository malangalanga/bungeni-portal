#
#  Scans a versions.cfg file of a buildout for product versions in a package index
#  If the product version does not exist in the package index (a simple http 200 = success check)
#  the script flags the product as missing
#
import sys
from configobj import ConfigObj
from httplib import HTTP
from urlparse import urlparse

allowed_ext = ['.tar.gz', '.tgz', '.zip']
py_ver_ext = { "2.4":"-py2.4.egg", "2.5":"-py2.5.egg"}

def checkLink(url):
	parsedURL = urlparse(url)
	httpConn = HTTP(parsedURL[1])
	httpConn.putrequest('HEAD',parsedURL[2])
	httpConn.endheaders()
	if httpConn.getreply()[0] == 200: return 1
	else: return 0


def checkVer(vFile, pURL, pyVer):
	print "in Checkver " + vFile
	missing_products = []
	allowed_ext.append(py_ver_ext[pyVer])
	config = ConfigObj(vFile)
	iversions = config['versions']
	for prod in iversions.keys():
		print 'checking ' + prod + ' .....'
		prod_exists = 0
		for ext in allowed_ext:
			if prod_exists == 0:
				prod_url = pURL + "/" + prod+"/" + prod + "-" + iversions[prod]+ext
				print '\tchecking ' + prod_url
				link_exists = checkLink(prod_url)
				if (link_exists == 1) :
					print '\t\tfound ' + prod_url
					prod_exists = 1
				else:
					print '\t\tnot found ' + prod_url
		if prod_exists == 0:
			print 'adding missing ' + prod + ' == ' + iversions[prod]
			missing_products.append(prod + ' == ' + iversions[prod])
	print 'Missing Products = ' + str(len(missing_products))
	for missing in missing_products:
		print missing	



if __name__ == '__main__':
	if (len(sys.argv) == 4 ):
		versionsFile = sys.argv[1]
		packageURL = sys.argv[2]
		pythonVersion = sys.argv[3]
		checkVer(versionsFile,packageURL, pythonVersion)
	else:
		print 'Required parameters : <versions.cfg file> <package url to check for versions> <python version 2.4 / 2.5> '

