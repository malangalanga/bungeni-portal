import bungeni


def essentials():
	"""
	Installs reqd OS packages as specified in distro.ini
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
	Build python imaging for Python 2.5 and 2.4
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.build_imaging()


def setup_pylibs():
	"""
	Install setuptools & supervisor  Pythons(2.5,2.4)
	"""
	bungenipre = bungeni.Presetup()
	bungenipre.required_pylibs()




def bungeni_setup():
	"""
	Checks out  & bootstrap bungeni source 
	"""
	tasks = bungeni.BungeniTasks()
	tasks.setup()

def bungeni_install():
	"""
	Checkout,bootstrap and build bungeni
	"""
	tasks = bungeni.BungeniTasks()
	tasks.setup()
	tasks.build()
	tasks.setupdb()

def bungeni_local_config():
	"""
	Generate a local buildout configuration.
	This is relevant only if you are using a local cache
	"""
	tasks = bungeni.BungeniTasks()
	tasks.local_config()


def bungeni_build():
	"""
	Runs the bungeni buildout
	"""
	tasks = bungeni.BungeniTasks()
	tasks.build()

def bungeni_setupdb():
	"""
	Sets up the postgresql db
	"""
	tasks = bungeni.BungeniTasks()
	tasks.setupdb()
	
def bungeni_update():
        """
        Update the bungeni source
 	"""
	tasks = bungeni.BungeniTasks()
	tasks.update()

def bungeni_build_opt():
	"""
	Runs an optimistic bungeni buildout (-N)
	"""
	tasks = bungeni.BungeniTasks()
	tasks.build_opt()

def supervisord_config():
	"""
	Generates the supervisor configuration
	"""
	pre = bungeni.Presetup()
	pre.supervisord_config()	

def portal_install():
	"""
	Setup and builds the portal
	"""
	tasks = bungeni.PortalTasks()
	tasks.setup()
	tasks.build()

def portal_build():
	"""
	Build the portal
	"""
	tasks = bungeni.PortalTasks()
	tasks.build()	

def portal_setup():
	"""
	Checkout and bootstrap portal source
	"""
	tasks = bungeni.PortalTasks()
	tasks.setup()


def __check(tasks):
	missing = tasks.check_versions()
	print len(missing), " packages"
	if len(missing) > 0 :
	    print "\n".join(missing)

def portal_check():
	"""
	Check missing packages for portal.buildout
	"""
	tasks = bungeni.PortalTasks()
	__check(tasks)

def bungeni_check():
	"""
	Check missing packages for bungeni.buildout
	"""
	tasks = bungeni.BungeniTasks()
	__check(tasks)

def start_bungeni():
	"""
	Start bungeni
	"""
	service = bungeni.Services()
	service.start_service("bungeni")

def stop_bungeni():
	"""
	Stop bungeni
	"""
	service = bungeni.Services()
	service.stop_service("bungeni")


def start_portal():
	"""
	Start the portal
	"""
	service = bungeni.Services()
	service.start_service("portal")


def stop_portal():
	"""
	Stop the portal
	"""
	service = bungeni.Services()
	service.stop_service("portal")


def start_postgres():
	"""
	Start postgres
	"""
	service = bungeni.Services()
	service.start_service("postgres")

def start_monitor():
	"""
	Start the supervisord service
	"""
	service = bungeni.Services()
	service.start_monitor()

def stop_monitor():
	"""
	Stop the supervisord service
	"""
	service = bungeni.Services()
	service.stop_monitor()






