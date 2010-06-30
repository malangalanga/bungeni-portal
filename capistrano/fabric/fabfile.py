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
