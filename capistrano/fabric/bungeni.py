from fabric.api import run,sudo, env

class OsInfo:
	def __init__(self):
		pass

	def release_id(self):
		output = run("lsb_release --id -s")
		return output

	def release_no(self):
		output = run("lsb_release --r -s")
		return output


class OsEssentials:
        def __init__(self):
                pass
	
	def get_reqd_libs(self, dist_id, dist_rel):
		return self.requiredLibs[dist_id+"-"+dist_rel]


        requiredLibs = {
                        'Ubuntu-10.04' : [
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
                        'Ubuntu-8.04' : [
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
		
		



class BungeniPresetup:

	def __init__(self):
		pass

	def presetup(self):
		pass

	def essentials(self):
		osInfo = OsInfo()
		osEssent = OsEssentials()
		liLibs = osEssent.get_reqd_libs(osInfo.release_id(), osInfo.release_no())
		sudo("apt-get install " + " ".join(liLibs))

		


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



