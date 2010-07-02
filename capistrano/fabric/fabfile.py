import bungeni


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


def portal_install():
	tasks = bungeni.PortalTasks()
	tasks.setup()
	tasks.build()
		
