from fabric.api import run,env

class OsInfo:
	def __init__(self):
		pass

	def release_id(self):
		output = run("lsb_release --id -s")
		return output

	def release_no(self):
		output = run("lsb_release --r -s")
		return output




class BungeniPresetup:

	def __init__(self):
		pass

	def presetup(self):
		pass


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
	print "I am " + osInfo.release_id() + " " + osInfo.release_no()


