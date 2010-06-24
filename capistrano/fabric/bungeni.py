from fabric.api import run,sudo, env
from configobj import ConfigObj

"""
Class to store util functions
""" 
class Utils:

	def __init__(self):
		pass

	"""
	Returns the basename of a url or path
	"""
	def get_basename(self, url_or_filepath):
		from posixpath import basename
		return basename(url_or_filepath)



"""
Returns information about the operating system
"""
class OsInfo:

	def __init__(self):
	"""
	Initialize the release id and release number variables
	"""
		self.release_id = ''
		self.release_no = ''

	"""
	Returns the distribution name for the operating system. Requires lsb_release on the operating system
	"""
	def get_release_id(self):
		if (len(self.release_id) == 0 ):
			self.release_id = run("lsb_release --id -s")

		return self.release_no

	"""
	Returns the version of the distribution of the operating system. Requires lsb_release on the operating system
	"""
	def get_release_no(self):
		if (len(self.release_no) == 0):
			self.release_no = run("lsb_release --r -s")

		return self.release_no


"""
Provides info about required packages for a specific operating system
"""
class OsEssentials:
        def __init__(self):
                pass
	"""
	Returns the list of required package names based on distribution
	"""	
	def get_reqd_libs(self, dist_id, dist_rel):
		return self.requiredLibs[dist_id][dist_rel]

	"""
	Returns the installation command for packages based on distribution
	"""
	def get_install_method(self, dist_id) :
		return self.installMethods[dist_id]

	"""
	Describes the different installation mechanisms by distribution 
	"""
	installMethods = {
			  'Ubuntu' : 'apt-get install ',
			  'Debian' : 'apt-get install ' ,
			  'Suse' : 'yum install ',
			  'Redhat' : 'rpm -Uvh ' 
			 }	


	"""
	Identifies required package names by distribution name and distribution version
	"""
        requiredLibs = {
                        'Ubuntu' : {
					'8.04' : 
						[
						"wget",
						"zip",
						"unzip",
						"build-essential", # for building from source
						"libjpeg62-dev", # for python
						"libfreetype6-dev", # for python
						"libbz2-dev", # for python bz2 processing
						"libxslt1-dev", # for python lxml
						"libxml2-dev", # for python lxml
						"libpng12-dev", # for python
						"openssl", # for python
						"libopenssl-dev", # for python
						"bison",  # for postgresql
						"flex" , # for postgresql
						"libreadline5-dev" , # for postgresql
						"zlib1g-dev" , # for postgresql
						"libtool" , # for svn
						"automake" ,  # for svn
						"autoconf" , # for svn
						"libsqlite3-dev", #for python unit tests
						"uuid-dev", # for ubuntu 9.04 xapian
						"openoffice.org-headless", #for generating pdf reports
						"python-uno", #for generating pdf reports
						"libtidy-dev" #required by tidy
						],
					'10.04' :
						[
						"wget",
						"zip",
						"unzip",
						"build-essential", # for building from source
						"libjpeg62-dev", # for python
						"libfreetype6-dev", # for python
						"libbz2-dev", # for python bz2 processing
						"libxslt1-dev", # for python lxml
						"libxml2-dev", # for python lxml
						"libpng12-dev", # for python
						"openssl", # for python
						"libssl-dev", # for python
						"bison",  # for postgresql
						"flex" , # for postgresql
						"libreadline5-dev" , # for postgresql
						"zlib1g-dev" , # for postgresql
						"libtool" , # for svn
						"automake" ,  # for svn
						"autoconf" , # for svn
						"libsqlite3-dev", #for python unit tests
						"uuid-dev", # for ubuntu 9.04 xapian
						"openoffice.org-headless", #for generating pdf reports
						"python-uno", #for generating pdf reports
						"libtidy-dev" #required by tidy
						],
					}
				}
		
		
"""
Provides access to the bungeni.ini build configuration file
"""
class BungeniConfigReader:

	def __init__(self):
		self.config = ConfigObj("bungeni.ini")

	def get_config(self, config_name):
		return self.config[config_name]
	
			

"""
Captures build specific configuration information
"""
class BungeniConfigs:

	def __init__(self):
		"""
		Required initializations
		"""
		self.commonutils = Utils()
		"""
		Required build parameters - setup paths etc.
		""" 
		self.bungeniConfig = BungeniConfigReader()
		self.user_build_root = get_config('system_root') + '/cbild'
		self.user_install_root = get_config('system_root') + '/cinst'
		self.user_python25_home = self.user_install_root + "/python25"
		self.user_python25 = self.user_python25_home + "/bin/python"
		self.user_python24_home = self.user_install_root + "/python24"
		self.user_python24 = self.user_python24_home + "/bin/python"
		self.user_bungeni = self.user_install_root + "/bungeni"
		""" 
		Python 2.5 build parameters 
		"""
		self.user_python25_build_path = self.user_build_root + "/python25"
		self.user_python25_runtime = self.user_install_root + "/python25"
		self.python25_download_file = self.commonutils.get_basename(python25_install_url)
		""" 
		Python 2.4 build parameters 
		"""
		self.user_python24_build_path = self.user_build_root + "/python24"
		self.user_python24_runtime = self.user_install_root + "/python24"
		self.python24_download_file = self.commonutils.get_basename(python25_install_url)
		"""
		Supervisord 
		"""
		self.supervisord = self.user_python_home + "/bin/supervisord"
		self.supervisorctl = self.user_python_home + "/bin/supervisorctl"




"""
This class does the pre-configuration and environment setup for installing bungeni
"""
class BungeniPresetup:


	def __init__(self):
		pass

	def presetup(self):
		pass

	def essentials(self):
		osInfo = OsInfo()
		osEssent = OsEssentials()
		"""
		Returns the required libraries for this operating system
		"""
		liLibs = osEssent.get_reqd_libs(osInfo.get_release_id(), osInfo.get_release_no())
		"""
		Install the required packages using the specific installation method.
		"""
		sudo(osEssent.get_install_method(osInfo.get_release_id()) + " ".join(liLibs))

		


class BungeniTasks:
	def __init__(self):
		pass


class PlonePresetup:
	def __init__(self):
		pass


class PloneTasks:
	def __init__(self):
		pass

	



def presetup():
	osInfo = OsInfo()
	osEssent = OsEssentials()
	print "I am " + osInfo.release_id() + " " + osInfo.release_no()
	print "Required = " + str(osEssent.get_reqd_libs(osInfo.release_id(), osInfo.release_no()))
	bungenipre = BungeniPresetup()
	bungenipre.essentials()

def read_configs():
	pass




