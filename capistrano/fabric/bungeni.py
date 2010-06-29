from fabric.api import run,sudo,cd,env
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

	def get_basename_prefix(self, url_or_filepath):
		from posixpath import basename
		from os import path
		afile = url_or_filepath
		while(True):
			l = path.splitext(afile)[0]
			if (l[1] == ''):
				afile = l[0]
				break
			else:
				afile = l[0]
		return basename(afile)



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

	def get_config(self, section_name, config_name):
		return self.config[section_name][config_name]
	
			

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
		self.cfg = BungeniConfigReader()
		self.gandi_deploy = self.cfg.get_config('global','gandi_deploy')
		self.user_build_root = self.cfg.get_config('global','system_root') + '/cbild'
		self.user_install_root = self.cfg.get_config('global','system_root') + '/cinst'
		self.linux_headers = 'linux-headers-`uname -r`'
		self.user_python25_home = self.user_install_root + "/python25"
		self.user_python25 = self.user_python25_home + "/bin/python"
		self.user_python24_home = self.user_install_root + "/python24"
		self.user_python24 = self.user_python24_home + "/bin/python"
		self.user_bungeni = self.user_install_root + "/bungeni"
		""" 
		Python 2.5 build parameters 
		"""
		self.python25_install_url = self.cfg.get_config('python25','download_url')
		self.user_python25_build_path = self.user_build_root + "/python25"
		self.user_python25_runtime = self.user_install_root + "/python25"
		self.python25 = self.user_python25_runtime + "/bin/python"
		self.python25_download_file = self.commonutils.get_basename(self.python25_install_url)
		self.python25_src_dir = self.commonutils.get_basename_prefix(self.python25_install_url)
		self.python25_download_command = self.get_download_command(self.python25_install_url)
		""" 
		Python 2.4 build parameters 
		"""
		self.python24_install_url = self.cfg.get_config('python24','download_url')
		self.user_python24_build_path = self.user_build_root + "/python24"
		self.user_python24_runtime = self.user_install_root + "/python24"
		self.python24 = self.user_python24_runtime + "/bin/python"
		self.python24_download_file = self.commonutils.get_basename(self.python24_install_url)
		self.python24_src_dir = self.commonutils.get_basename_prefix(self.python24_install_url)
		self.python24_download_command = self.get_download_command(self.python24_install_url)
		"""
		Python Imaging parameters 
		"""
		self.python_imaging_download_url = self.cfg.get_config('imaging','download_url')
		self.python_imaging_build_path = self.user_build_root + "/imaging"
		self.python_imaging_download_command = self.get_download_command(self.python_imaging_download_url)
		self.python_imaging_download_file = self.commonutils.get_basename(self.python_imaging_download_url)
		self.python_imaging_src_dir = self.commonutils.get_basename_prefix(self.python_imaging_download_file)
		"""
		Supervisord 
		"""
		self.supervisord = self.user_python25_home + "/bin/supervisord"
		self.supervisorctl = self.user_python25_home + "/bin/supervisorctl"

	def get_download_command (self, strURL):
		if (strURL.startswith("http") or strURL.startswith("ftp")):
			return "wget " + strURL
		else:
			return "cp " + strURL + " ."
	

	



"""
This class does the pre-configuration and environment setup for installing bungeni
"""
class Presetup:


	def __init__(self):
		self.cfg = BungeniConfigs()
		self.osinfo = OsInfo()
		self.ossent = OsEssentials()

	def presetup(self):
		pass

	def essentials(self):
		"""
		Returns the required libraries for this operating system
		"""
		liLibs = self.ossent.get_reqd_libs(osinfo.get_release_id(), osinfo.get_release_no())
		"""
		Install the required packages using the specific installation method.
		"""
		sudo(self.ossent.get_install_method(osinfo.get_release_id()) + " ".join(liLibs))
		if (self.cfg.gandi_deploy <> True) :
			"""
			This is not a gandi deployment
			"""
			sudo(ossent.get_install_method(osinfo.get_release_id()) + " " + self.cfg.linux_headers


					
	"""
	Builds Python 2.5 from source 	
	"""
	def build_py25(self):
		run("mkdir -p " + self.cfg.user_python25_build_path)
		run("rm -rf " + self.cfg.user_python25_build_path + "/*.*" )
		run("mkdir -p " + self.cfg.user_python25_runtime)
		with cd(self.cfg.user_python25_build_path):
			run(self.cfg.python25_download_command)
			run("tar xvzf " + self.cfg.python25_download_file)
			with cd(self.cfg.python25_src_dir):
				run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix=" + self.cfg.user_python25_runtime + " USE=sqlite")
				run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make")
				run("make install")

	"""
	Builds Python 2.4 from source
	"""
	def build_py24(self):
		run("mkdir -p " + self.cfg.user_python24_build_path)
		run("rm -rf " + self.cfg.user_python24_build_path + "/*.*" )
		run("mkdir -p " + self.cfg.user_python24_runtime)
		with cd(self.cfg.user_python24_build_path):
			run(self.cfg.python24_download_command)
			run("tar xvzf " + self.cfg.python24_download_file)
			with cd(self.cfg.python24_src_dir):
				run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix=" + self.cfg.user_python24_runtime )
				run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make")
				run("make install")
	
	"""
	Builds Python imaging from source
	Installs it for both Python 2.4 and 2.5
	"""
	def build_imaging(self):
		run("mkdir -p " + self.cfg.python_imaging_build_path)
		with cd(self.cfg.python_imaging_build_path):
			run("rm -rf " + self.cfg.python_imaging_download_file)
			run("wget " + self.cfg.python_imaging_download_url)	
			run("rm -rf " + self.cfg.python_imaging_src_dir)
			run("tar xvzf " + self.cfg.python_imaging_download_file)
			with cd(self.cfg.python_imaging_src_dir):
				if (os.path.isfile(self.cfg.python25):
					run(self.cfg.python25 +" setup.py build_ext -i")
					run(self.cfg.python25 +" setup.py install")
				if (os.path.isfile(self.cfg.python24):
					run(self.cfg.python24 + " setup.py build_ext -i")
					run(self.cfg.python24 + " setup.py install")



	


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
	read_configs()

def read_configs():
	configs = BungeniConfigReader()
	print configs.get_config("global", "system_root")
	print configs.get_config("bungeni", "build")




