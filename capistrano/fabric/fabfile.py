import bungeni


def essentials():
	"""
	Installs the required operating system packages as specified in distro.ini
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.essentials()

"""
Build python 2.5
"""
def build_python25():
	"""
	Builds Python 2.5 from source
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.build_py25()
	
"""
Build python 2.4
"""	
def build_python24():
	"""
	Builds Python 2.4 from source
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.build_py24()


def build_imaging():
	"""
	Builds python imaging extensions for Python 2.5 and 2.4
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.build_imaging()


def setup_pylibs():
	"""
	Installs setuptools and supervisor for the built Pythons (2.5 and 2.4)
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.required_pylibs()




def bungeni_checkout():
	"""
	Checks out bungeni source 
	"""
	tasks = bungeni.BungeniTasks()
	tasks.src_checkout()
	tasks.bootstrap()



def bungeni_bo_full():
	"""
	Runs the bungeni buildout
	"""
	tasks = bungeni.BungeniTasks()
	tasks.buildout_full()

def bungeni_bo_opt():
	tasks = bungeni.BungeniTasks()
	tasks.buildout_opt()

def supervisord_config():
	pre = bungeni.Presetup()
	pre.supervisord_config()	

def portal_install():
	tasks = bungeni.PortalTasks()
	tasks.setup()
	tasks.build()

def portal_build():
	tasks = bungeni.PortalTasks()
	tasks.build()	

def __check(tasks):
	missing = tasks.check_versions()
	print len(missing), " packages"
	if len(missing) > 0 :
	    print "\n".join(missing)

def portal_check():
	tasks = bungeni.PortalTasks()
	__check(tasks)

def bungeni_check():
	tasks = bungeni.BungeniTasks()
	__check(tasks)


