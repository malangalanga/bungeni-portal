from fabric.api import *
from fabric.context_managers import settings
from ConfigParser import SafeConfigParser as _scg
from required import Templates as _tmpl
import os

__debpack_scripts__ = ["preinst", "postinst", "prerm", "postrm"]


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


def _build_archive(archive_name,  update_config_folder):
    archive = "%s.tar.gz" % archive_name
    run("tar -czf %s  -T %s/update.include -X %s/update.exclude " % (archive, update_config_folder, update_config_folder))
    return os.path.join(env.cwd, archive)

def _md5sums(target_folder):
    with cd(target_folder):
        run("cd ./debian && find .  -type f -not -path \"*.svn*\"  | grep -v 'DEBIAN'  | xargs md5sum > ../md5sums")
        run("sed -i 's|./opt|opt|g' md5sums")
        run("mv md5sums debian/DEBIAN")

def _dpkg_deb(target_folder, archive_name):
    with cd(target_folder):
        run("dpkg-deb --build debian")
        run("mv debian.deb ../%s.deb" % archive_name)

def _get_size(update_config_folder):
    with cd(update_config_folder):
        size = run("echo $(du -sc $(tr '\\n' ' ' < ./update.include) -X ./update.exclude | tail -1 | awk -F ' ' '{print $1}')")
        return size

    
def build_update(in_folder, version):
    
    folder_name = "bungeni_update_%s" % version
    update_config_folder = os.path.join(in_folder, folder_name)
     
    if not os.path.exists(update_config_folder):
        print "Update configuration folder not found, aborting !"
        return
    
    cfg = __UpdateConfigParser(
        os.path.join(update_config_folder, "update.ini")
    )
    ver =  cfg.get_update_version()

    depends = cfg.get_update_depends()
    #in_folder is the source folder
    #target folder is the target folder
    parent_in_folder = os.path.realpath(
        os.path.join(in_folder, "..")
    )
    target_folder = os.path.realpath(
        os.path.join(parent_in_folder, folder_name)
    )
    with cd(parent_in_folder):
         archive_path = _build_archive(folder_name, update_config_folder)              
         run("mkdir -p %s" % target_folder)
         size = _get_size(update_config_folder)
         template_map = {
               "size": size,
               "version": ver,
               "arch": __platform(),
               "depends": ",".join(depends)
         }
         with cd(target_folder):
             run("mkdir -p debian/DEBIAN")
             for file in __debpack_scripts__:
                 file_path_in_config = os.path.join(update_config_folder, file)
                 if os.path.exists(file_path_in_config):
                    run("cp %s ./debian/DEBIAN" % file_path_in_config)
             with cd("debian/DEBIAN"):
                t = _tmpl()
                t.new_file(
                    os.path.join(in_folder, "control.tmpl"),
                    template_map,
                    env.cwd
                )
         
         run("tar xvf %s -C %s" % (archive_path, os.path.join(target_folder, "debian")))
         _md5sums(target_folder)
         _dpkg_deb(target_folder, folder_name)
              
def setup_version():
    run("echo $(date +%Y%m%d)")
    

def platform():
    print __platform()



