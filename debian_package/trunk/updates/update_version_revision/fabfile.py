from fabric.api import *
from fabric.context_managers import settings
from ConfigParser import SafeConfigParser as _scg
from required import Templates as _tmpl
import os


class __UpdateConfigParser():

    def __init__(self, file):
        self.cfg = _scg()
        self.cfg.read(file)
    
    def get_update_version(self):
        return self.cfg.get("update", "version")
        

    def get_update_depends(self):
        ldepends = self.cfg.get("update", "depends").split("\n")
        return filter(None, ldepends)


def __platform():
    long_bit = run("getconf LONG_BIT")
    if long_bit == "64":
        return "amd64"
    else:
        return "i386" 


def _build_archive(arch_name):
    archive = "%s.tar.gz" % arch_name
    run("tar -czf %s  -T ../update.include -X ../update.exclude " % archive)

    
def build_update(in_folder):
    cfg = __UpdateConfigParser("update.ini")
    ver = cfg.get_update_version()
    depends = cfg.get_update_depends()
    folder_name = "bungeni_update_%s" % ver
    with cd(in_folder):
       run("mkdir -p %s" % folder_name)
       with cd(folder_name):
          run("cp -R ../debian .")
          _build_archive(folder_name)              
          with cd("debian/DEBIAN"):
             t = _tmpl()
             #    
              
def setup_version():
    run("echo $(date +%Y%m%d)")
    

def platform():
    print __platform()



