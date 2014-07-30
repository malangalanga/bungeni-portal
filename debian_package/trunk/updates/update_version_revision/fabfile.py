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


def _build_archive(archive_name, source_folder):
    archive = "%s.tar.gz" % archive_name
    run("tar -czf %s  -T %s/update.include -X %s/update.exclude " % (archive, source_folder, source_folder))
    return os.path.join(env.cwd, archive)

def _get_size():
    size = run("echo $(du -sc $(tr '\\n' ' ' < ./update.include) -X ./update.exclude | tail -1 | awk -F ' ' '{print $1}')")
    return size

    
def build_update(in_folder):
    cfg = __UpdateConfigParser("update.ini")
    ver = cfg.get_update_version()
    depends = cfg.get_update_depends()
    folder_name = "bungeni_update_%s" % ver
    #in_folder is the source folder
    #target folder is the target folder
    parent_in_folder = os.path.realpath(
        os.path.join(in_folder, "..")
    )
    target_folder = os.path.realpath(
        os.path.join(parent_in_folder, folder_name)
    )
    with cd(parent_in_folder):
         archive_path = _build_archive(folder_name, in_folder)              
         with cd(in_folder):
            run("mkdir -p %s" % target_folder)
            size = _get_size()
            template_map = {
               "size": size,
               "version": ver,
               "arch": __platform(),
               "depends": ",".join(depends)
            }
            with cd(target_folder):
              run("cp -R %s ." % os.path.join(in_folder, "debian"))
              with cd("debian/DEBIAN"):
                 t = _tmpl()
                 t.new_file(
                     os.path.join(env.cwd, "control.tmpl"),
                     template_map,
                     env.cwd
                 )
         run("tar xvf %s -C %s" % (archive_path, os.path.join(target_folder, "debian")))
              
def setup_version():
    run("echo $(date +%Y%m%d)")
    

def platform():
    print __platform()



