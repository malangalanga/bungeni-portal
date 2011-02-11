#
#  Scans a versions.cfg file of a buildout for product versions in a package index
#  If the product version does not exist in the package index (a simple http 200 = success check)
#  the script flags the product as missing
#
import sys
from ConfigParser import SafeConfigParser
from httplib import HTTP
from urlparse import urlparse

class CheckVersions():
	def __init__(self,versions_file, package_url, python_version):
		"""
		versions_cfg - the versions configuration file
		package_index - the URL of the package index
		python version - 2.4 or 2.5
		"""
	        print "versions ", versions_file , "\npackage_url ", package_url, "\npython_version " , python_version
		self.versions_cfg = versions_file
		self.package_index = package_url
		self.python_version = python_version
		self.allowed_ext = ['.tar.gz', '.tgz', '.zip']
		self.py_ver_ext = { "2.4":"-py2.4.egg", "2.5":"-py2.5.egg"}

	def checkLink(self, url):
		parsedURL = urlparse(url)
		httpConn = HTTP(parsedURL[1])
		httpConn.putrequest('HEAD',parsedURL[2])
		httpConn.endheaders()
		if httpConn.getreply()[0] == 200: return 1
		else: return 0


	def checkVersion(self):
		#print "in Checkver " + self.versions_cfg
		missing_products = []
		self.allowed_ext.append(self.py_ver_ext[self.python_version])
		config = SafeConfigParser()
		config.optionxform = lambda orig: orig
                config.read(self.versions_cfg)
	        """
	        returns a tuple list of key-value pairs
  		"""
	        iversions = config.items('versions')
		#print iversions
		iversions_keys = [value[0] for value in iversions]
		for prod in iversions_keys:
			print 'checking ' + prod + ' .....'
			prod_exists = 0
			for ext in self.allowed_ext:
				if prod_exists == 0:
					prod_url = self.package_index + "/" + prod+"/" + prod + "-" + config.get('versions',prod)+ext
					print '\tchecking ' + prod_url
					link_exists = self.checkLink(prod_url)
					if (link_exists == 1) :
						#print '\t\tfound ' + prod_url
						prod_exists = 1
					else:
						pass
						#print '\t\tnot found ' + prod_url
			if prod_exists == 0:
				print 'adding missing ' + prod + ' == ' + config.get('versions',prod)
				missing_products.append(prod + ' == ' + config.get('versions',prod))
		#print 'Missing Products = ' + str(len(missing_products))
	        return missing_products		


"""
if __name__ == '__main__':
	if (len(sys.argv) == 4 ):
		versionsFile = sys.argv[1]
		packageURL = sys.argv[2]
		self.python_version = sys.argv[3]
		checkVer(versionsFile,packageURL, self.python_version)
	else:
		print 'Required parameters : <versions.cfg file> <package url to check for versions> <python version 2.4 / 2.5> '
"""
