#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
from fabric.api import *
from fabric.colors import red, green
from fabric.contrib.files import exists
from ConfigParser import SafeConfigParser
import checkversions


class Utils:

    """
    Class to store util functions
    """

    def __init__(self):
        """
        Defines the allowed archive extensions and their extraction methods
        """

        self.allowed_archive_exts = [".tar.gz", ".tgz"]
        self.file_extract_methods = {".tar.gz": "tar xvf ",
                ".tgz": "tar xvf "}

    def get_basename(self, url_or_filepath):
        """
        Returns the basename of a url or path
        """

        from posixpath import basename
        return basename(url_or_filepath)

    def get_basename_prefix(self, url_or_filepath):
        filename = self.get_basename(url_or_filepath)
        for ext in self.allowed_archive_exts:
            if filename.endswith(ext):
                return filename.replace(ext, "")
        return filename

    def parse_boolean(self, boolval):
        """
        Parses a boolean string from the config file into a Boolean type
        """

        bool_map = {"true": True, "false": False}
        if boolval == True or boolval == False:
            return boolval
        return bool_map[boolval.strip().lower()]

    def get_fab_path(self):
        """
        Returns the parent path of the currently running fabric file
        """

        return os.path.abspath(os.path.join(env.real_fabfile, ".."))


class OsInfo:

    """
    Returns information about the operating system.
    This information can be overriden using the distro_override 
    configuration parameter
    """

    def __init__(self, distro_override):
        """
        Initialize the release id and release number variables
        """

        if len(distro_override.strip()) == 0:
            self.release_id = self.__get_release_id()
            self.release_no = self.__get_release_no()
        else:
            l_distro = distro_override.split(":")
            self.release_id = l_distro[0]
            self.release_no = l_distro[1]

    def __get_release_id(self):
        """
        Returns the distribution name for the operating system. 
        Requires lsb_release on the operating system
        """

        rel_id = run("lsb_release --id -s")
        return rel_id

    def __get_release_no(self):
        """
        Returns the version of the distribution of the operating system. 
        Requires lsb_release on the operating system
        """

        rel_no = run("lsb_release --r -s")
        return rel_no


class OsEssentials:

    """
    Provides info about required packages for a specific operating system
    Reads the required packages from distro.ini
    Also checks to see if the current OS is installed on a Gandi server
    """

    def __init__(self):
        utils = Utils()
        distro_ini = utils.get_fab_path() + "/distro.ini"
        self.distro = SafeConfigParser()
        self.distro.read(distro_ini)

    def __parse_config(self, dist_id, dist_rel):
        pkgs = self.distro.get(dist_id, dist_rel)
        lipkgs = pkgs.splitlines()

        # remove blank entries in list

        lipkgs = filter(lambda x: len(x) > 0, lipkgs)

        # remove items that start with #

        lipkgs = filter(lambda x: not x.startswith("#"), lipkgs)
        return lipkgs

    def is_gandi_server(self):
        """
        Checks if this is a gandi server by looking for the /etc/gandi folder
        """

        return os.path.exists("/etc/gandi")

    def get_reqd_libs(self, dist_id, dist_rel):
        """
        Returns the list of required package names based on distribution
        """

        return self.__parse_config(dist_id, dist_rel)

    def get_install_method(self, dist_id):
        """
        Returns the installation command for packages based on distribution
        """

        return self.installMethods[dist_id]

    installMethods = {
        "Ubuntu": "apt-get install -y ",
        "Debian": "apt-get install -y ",
        "Suse": "yum install ",
        "Redhat": "rpm -Uvh ",
        }


class BungeniConfigReader:

    """
    Provides access to the bungeni.ini build configuration file
    """

    def __init__(self, inifile):
        self.config = SafeConfigParser()
        self.config.read(inifile)

    def get_config(self, section_name, config_name):
        if self.config.has_section(section_name):
            if self.config.has_option(section_name, config_name):
                return self.config.get(section_name,
                        config_name).strip()
            else:
                print "warning : section [", section_name, \
                    "] does not have option name ", config_name, " !!!!"
                return ""
        else:
            print "warning: section [", section_name, \
                "] does not exist !!!"
            return ""


class BungeniConfigs:

    """
    Captures build specific configuration information
    """

    def __init__(self):
        """
        Required initializations
        """

        self.utils = Utils()
        self.cfg = BungeniConfigReader("setup.ini")
        self.svn_user = self.cfg.get_config("scm", "user")
        self.svn_password = self.cfg.get_config("scm", "pass")
        self.verbose = \
            self.utils.parse_boolean(self.cfg.get_config("global",
                "verbose"))
        self.development_build = \
            self.utils.parse_boolean(self.cfg.get_config("global",
                "development_build"))
        self.app_host = self.cfg.get_config("global", "app_host")
        self.supervisor_host = self.cfg.get_config("supervisor",
                "host")
        self.supervisor_port = self.cfg.get_config("supervisor",
                "port")
        self.local_cache = \
            self.utils.parse_boolean(self.cfg.get_config("global",
                "local_cache"))
        self.user_build_root = self.cfg.get_config("global",
                "system_root") + "/cbild"
        self.user_install_root = self.cfg.get_config("global",
                "system_root") + "/cinst"
        self.distro_override = self.cfg.get_config("global",
                "distro_override")
        self.linux_headers = "linux-headers-`uname -r`"
        # python 2.6
        self.user_python26_home = self.user_install_root + "/python26"
        self.python26 = self.user_python26_home + "/bin/python"
        # python 2.5
        self.user_python25_home = self.user_install_root + "/python25"
        self.user_python25 = self.user_python25_home + "/bin/python"
        # python 2.4
        self.user_python24_home = self.user_install_root + "/python24"
        self.user_python24 = self.user_python24_home + "/bin/python"
        # bungeni, plone, portal
        self.user_bungeni = self.user_install_root + "/bungeni"
        self.user_plone = self.user_bungeni + "/plone"
        self.user_portal = self.user_bungeni + "/portal"
        self.user_config = self.user_install_root + "/config"
        self.user_logs = self.user_install_root + "/logs"
        self.user_pid = self.user_install_root + "/pid"
        # python setup 
        # 2.6    
        self.python26_install_url = self.cfg.get_config("python26",
                "download_url")
        self.user_python26_build_path = self.user_build_root \
            + "/python26"           
        self.python26_src_dir = \
            self.utils.get_basename_prefix(self.python26_install_url)
        self.python26_download_file = \
            self.utils.get_basename(self.python26_install_url)
        self.python26_download_command = \
            self.get_download_command(self.python26_install_url)
        # 2.5
        self.python25_install_url = self.cfg.get_config("python25",
                "download_url")
        self.user_python25_build_path = self.user_build_root \
            + "/python25"
        self.user_python25_runtime = self.user_install_root \
            + "/python25"
        self.python25 = self.user_python25_runtime + "/bin/python"
        self.python25_download_file = \
            self.utils.get_basename(self.python25_install_url)
        self.python25_src_dir = \
            self.utils.get_basename_prefix(self.python25_install_url)
        self.python25_download_command = \
            self.get_download_command(self.python25_install_url)
        self.python24_install_url = self.cfg.get_config("python24",
                "download_url")
        self.user_python24_build_path = self.user_build_root \
            + "/python24"
        self.user_python24_runtime = self.user_install_root \
            + "/python24"
        self.python24 = self.user_python24_runtime + "/bin/python"
        self.python24_download_file = \
            self.utils.get_basename(self.python24_install_url)
        self.python24_src_dir = \
            self.utils.get_basename_prefix(self.python24_install_url)
        self.python24_download_command = \
            self.get_download_command(self.python24_install_url)
        self.python_imaging_download_url = self.cfg.get_config("imaging",
            "download_url")
        self.python_imaging_build_path = self.user_build_root \
            + "/imaging"
        self.python_imaging_download_command = \
            self.get_download_command(self.python_imaging_download_url)
        self.python_imaging_download_file = \
            self.utils.get_basename(self.python_imaging_download_url)
        self.python_imaging_src_dir = \
            self.utils.get_basename_prefix(self.python_imaging_download_file)
        self.python_appy_download_url = self.cfg.get_config("appy",
            "download_url")
        self.python_appy_download_command = \
            self.get_download_command(self.python_appy_download_url)
        self.python_appy_download_file = \
            self.utils.get_basename(self.python_appy_download_url)
        # bungeni configuration parameters
        self.bungeni_repo = self.cfg.get_config("bungeni", "repo")
        self.bungeni_local_index = self.cfg.get_config("bungeni",
                "local_index")
        self.bungeni_dump_file = self.cfg.get_config("bungeni",
                "dump_file")
        self.bungeni_attachments_folder = self.cfg.get_config("bungeni",
                "attachments_folder")
        self.bungeni_attachments_archive = self.cfg.get_config("bungeni",
                "attachments_archive")
        self.bungeni_general_buildout_config = "buildout.cfg"
        self.bungeni_local_buildout_config = "bungeni_local.cfg"
        self.bungeni_deploy_ini = self.user_bungeni + "/bungeni.ini"
        self.bungeni_buildout_config = \
            (self.bungeni_general_buildout_config if self.local_cache
             == False else self.bungeni_local_buildout_config)
        self.bungeni_http_port = self.cfg.get_config("bungeni",
                "http_port")
        self.bungeni_admin_user = self.cfg.get_config("bungeni",
                "admin_user")
        self.bungeni_admin_password = self.cfg.get_config("bungeni",
                "admin_password")
        # plone configuration parameters
        self.plone_repo = self.cfg.get_config("plone", "repo")
        self.plone_local_index = self.cfg.get_config("plone",
                "local_index")
        self.plone_site_content = self.cfg.get_config("plone",
                "site_content")
        self.plone_general_buildout_config = "buildout.cfg"
        self.plone_local_buildout_config = "plone_local.cfg"
        self.plone_deploy_ini = self.user_plone + "/plone.ini"
        self.plone_buildout_config = \
            (self.plone_general_buildout_config if self.local_cache
             == False else self.plone_local_buildout_config)
        self.plone_http_port = self.cfg.get_config("plone", "http_port")
        # portal configuration parameters
        self.portal_repo = self.cfg.get_config("portal", "repo")
        self.portal_local_index = self.cfg.get_config("portal",
                "local_index")
        self.portal_general_buildout_config = "buildout.cfg"
        self.portal_local_buildout_config = "portal_local.cfg"
        self.portal_static_ini = self.user_portal + "/static.ini"
        self.portal_rules_xml_uri = "file:" + self.user_bungeni \
            + "/src/bungeni.main/bungeni/portal/static/themes/rules.xml"
        self.portal_theme = self.cfg.get_config("portal", "theme")
        self.portal_buildout_config = \
            (self.portal_general_buildout_config if self.local_cache
             == False else self.portal_local_buildout_config)
        self.portal_http_port = self.cfg.get_config("portal",
                "http_port")
        self.portal_static_port = self.cfg.get_config("portal",
                "static_port")
        self.portal_web_server_host = self.cfg.get_config("portal",
                "web_server_host")
        self.portal_web_server_port = self.cfg.get_config("portal",
                "web_server_port")
        # others :  postgresql, xapian
        self.postgresql_local_url = self.cfg.get_config("postgresql",
                "local_url")
        self.xapian_local_url = self.cfg.get_config("xapian",
                "local_url")
        self.xapian_bindings_local_url = \
            self.cfg.get_config("xapian-bindings", "local_url")
        self.postgresql_bin = self.user_bungeni \
            + "/parts/postgresql/bin"
        self.db_dump_update_script = self.utils.get_fab_path() \
            + "/scripts/upd-dbdump.sh"
        #custom 
        self.bungeni_custom_pth = "bungeni_custom.pth"
        self.custom_folder = self.cfg.get_config("custom",
                "folder")
        self.enabled_translations = self.cfg.get_config("custom",
                "enabled_translations").split(":")
        self.translatable_packages = self.cfg.get_config("custom",
                "translatable_packages").split(":")
        self.country_theme = self.cfg.get_config('custom', 'country_theme')
        # supervisor
        self.supervisorconf = self.user_config + "/supervisord.conf"



    def get_download_command(self, strURL):
        if strURL.startswith("http") or strURL.startswith("ftp"):
            return "wget %(download_url)s" % {"download_url": strURL}
        else:
            return "cp %(file_path)s ." % {"file_path": strURL}
    

class PythonConfigs:

    def __init__(self, cfg, config_name):
        self.cfg = cfg
        self.cfgreader = cfg.cfg
        self.python_ver = self.cfgreader.get_config(config_name, "python")
        self.python_home = self.get_python_home(config_name)
        self.python = self.python_home + "/bin/python"
        self.python_packages = self.python_home + "/lib/python" + self.python_ver + "/site-packages"

    def get_python_home(self, config_name):
        selected_python = self.cfgreader.get_config(config_name,"python")
        if selected_python == "2.6":
            return self.cfg.user_python26_home
        elif selected_python == "2.5":
            return self.cfg.user_python25_home
        elif selected_python == "2.4":
            return self.cfg.user_python24_home
        else:
            return self.cfg.user_python25_home




class Presetup:

    """
    This class does the pre-configuration and environment setup for 
    installing bungeni.
    Setup the required objects for this class
    cfg provides access to build config info
    osinfo provides info about the operating system for the build to
    automatically setup required packages
    ossent provides info about the required packages for bungeni 
    filtered by distro
    """

    def __init__(self):
        self.cfg = BungeniConfigs()
        self.osinfo = OsInfo(self.cfg.distro_override)
        self.ossent = OsEssentials()
        self.templates = Templates(self.cfg)

    def presetup(self):
        pass

    def essentials(self):
        """
        Returns the required libraries for this operating system
        """

        liLibs = self.ossent.get_reqd_libs(self.osinfo.release_id,
                self.osinfo.release_no)
        sudo(self.ossent.get_install_method(self.osinfo.release_id)
             + " ".join(liLibs))
        if not self.ossent.is_gandi_server():
            print "Installing Linux Headers"
            sudo(self.ossent.get_install_method(self.osinfo.release_id)
                 + " " + self.cfg.linux_headers)
        else:
            print "This server was identified as a Gandi virtual server"


    def build_py26(self):
        run("mkdir -p " + self.cfg.user_python26_build_path)
        run("rm -rf " + self.cfg.user_python26_build_path + "/*.*")
        run("mkdir -p " + self.cfg.user_python26_home)
        with cd(self.cfg.user_python26_build_path):
            run(self.cfg.python26_download_command)
            run("tar xvf " + self.cfg.python26_download_file)
            with cd(self.cfg.python26_src_dir):
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl \
                     ./configure --prefix=%(python_home)s USE=sqlite"\
                     % {"python_home":self.cfg.user_python26_home})
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make")
                run("make install")


    def build_py25(self):
        run("mkdir -p " + self.cfg.user_python25_build_path)
        run("rm -rf " + self.cfg.user_python25_build_path + "/*.*")
        run("mkdir -p " + self.cfg.user_python25_runtime)
        with cd(self.cfg.user_python25_build_path):
            run(self.cfg.python25_download_command)
            run("tar xvf " + self.cfg.python25_download_file)
            with cd(self.cfg.python25_src_dir):
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl \
                     ./configure --prefix=%(python_runtime)s USE=sqlite"\
                     % {"python_runtime":self.cfg.user_python25_runtime})
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make")
                run("make install")


    def build_py24(self):
        """
        Builds Python 2.4 from source
        """

        run("mkdir -p " + self.cfg.user_python24_build_path)
        run("rm -rf " + self.cfg.user_python24_build_path + "/*.*")
        run("mkdir -p " + self.cfg.user_python24_runtime)
        with cd(self.cfg.user_python24_build_path):
            run(self.cfg.python24_download_command)
            run("tar xvf " + self.cfg.python24_download_file)
            with cd(self.cfg.python24_src_dir):
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix="
                     + self.cfg.user_python24_runtime)
                run("CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make")
                run("make install")

    def build_imaging(self):
        """
        Builds Python imaging from source
        Installs it for both Python 2.4 and 2.5
        """

        run("mkdir -p " + self.cfg.python_imaging_build_path)
        with cd(self.cfg.python_imaging_build_path):
            run("rm -rf " + self.cfg.python_imaging_download_file)
            run(self.cfg.python_imaging_download_command)
            run("rm -rf " + self.cfg.python_imaging_src_dir)
            run("tar xvzf " + self.cfg.python_imaging_download_file)
            with cd(self.cfg.python_imaging_src_dir):
                if os.path.isfile(self.cfg.python26):
                    print self.cfg.python26 + " setup.py build_ext -i"
                    run(self.cfg.python26 + " setup.py build_ext -i")
                    run(self.cfg.python26 + " setup.py install")
                if os.path.isfile(self.cfg.python25):
                    print self.cfg.python25 + " setup.py build_ext -i"
                    run(self.cfg.python25 + " setup.py build_ext -i")
                    run(self.cfg.python25 + " setup.py install")
                if os.path.isfile(self.cfg.python24):
                    run(self.cfg.python24 + " setup.py build_ext -i")
                    run(self.cfg.python24 + " setup.py install")

    def __setuptools(self, pybin, pyhome):
        if os.path.isfile(pybin):
            with cd(pyhome):
                run("[ -f ./ez_setup.py ] && echo 'ez_setup.py exists' || wget http://peak.telecommunity.com/dist/ez_setup.py")
                run(pybin + " ./ez_setup.py")

    def setuptools(self):
        """
        Install setuptools for python
        """
        self.__setuptools(self.cfg.python26,
                          self.cfg.user_python26_home)
        self.__setuptools(self.cfg.python25,
                          self.cfg.user_python25_home)
        self.__setuptools(self.cfg.python24,
                          self.cfg.user_python24_home)

    def supervisor(self):
        """
        Install Supervisord
        """
        
        sup_pycfg = PythonConfigs(self.cfg,"supervisor")
        run(sup_pycfg.python_home + "/bin/easy_install supervisor"
            )
            
    def install_appy(self):
        """
        Install appy
        """
        bungeni_pycfg = PythonConfigs(self.cfg,"bungeni")
        with cd(bungeni_pycfg.python_packages):
            run(self.cfg.python_appy_download_command)
            run("unzip -o " + self.cfg.python_appy_download_file)
            run("rm -rf " + self.cfg.python_appy_download_file)
            
    def supervisord_config(self):
        """
        Generate a supervisord config file  using the installation template
        """

        sup_pycfg = PythonConfigs(self.cfg,"supervisor")
        template_map = {
            "user_bungeni": self.cfg.user_bungeni,
            "user_plone": self.cfg.user_plone,
            "user_portal": self.cfg.user_portal,
            "app_host": self.cfg.app_host,
            "supervisor_host": self.cfg.supervisor_host,
            "supervisor_port": self.cfg.supervisor_port,
            "user_config": self.cfg.user_config,
            "user_logs": self.cfg.user_logs,
            "user_pid":self.cfg.user_pid,
            "bungeni_ini": self.cfg.bungeni_deploy_ini,
            "plone_ini": self.cfg.plone_deploy_ini,
            "static_ini": self.cfg.portal_static_ini,
            }
        run("mkdir -p %s" % self.cfg.user_config)
        run("mkdir -p %s" % self.cfg.user_logs)
        run("mkdir -p %s" % self.cfg.user_pid)
        self.templates.new_file("supervisord.conf.tmpl", template_map,
                                self.cfg.user_config)

    def required_pylibs(self):
        """
        Installs required python libraries - setuptools and supervisor
        """

        self.setuptools()
        self.supervisor()

class SCM:

    """
    Interaction with SVN
    Does a secure checkout when devmode is set to True
    Does a http:// non updatable checkout when devmode is set to False
    Takes 5 input parameters - 
        devmode  - True / False indicatiing development mode
        user - svn user name
        password - svn password
        working_copy - path to working copy
        address - svn address of repository
    """

    def __init__(
        self,
        mode,
        address,
        user,
        password,
        workingcopy,
        ):
        self.devmode = mode
        self.user = user
        self.password = password
        self.address = address
        self.working_copy = workingcopy

    def checkout(self):
      """
      Checks out the source code either in dev-mode or anonymously
      """

      cmd = ""
      if self.devmode == True:
          print "Checking out in dev-mode with username = ", self.user
          cmd = "svn co https://%s --username=%s --password=%s %s" \
              % (self.address, self.user, self.password,
                 self.working_copy)
          self.svn_perm()
      else:
          print "Checkout out anonymously"
          cmd = "svn co http://%s %s" % (self.address,
                  self.working_copy)
          self.svn_perm()
      run(cmd)

    def update(self):
       """
       Updates the working copy
       """

       with cd(self.working_copy):
           self.svn_perm()
           run("svn up")

    def svn_perm(self):
       """
       Subversion can occasionaly ask the user to verify a https certificate 
       This method accepts the certificate temporarily
       """

       working_copy_map = {"working_folder": self.working_copy}
       if not os.path.exists("%(working_folder)s/svn_ans_t.txt"
                             % working_copy_map):
           run("echo 'p' > %(working_folder)s/svn_ans_t.txt"
               % working_copy_map)
       if self.devmode == True:
           svn_perm_map = {
               "repo": self.address,
               "working_folder": self.working_copy,
               "user": self.user,
               "password": self.password,
               }
           run("svn info https://%(repo)s --username=%(user)s --password=%(password)s <%(working_folder)s/svn_ans_t.txt"
                % svn_perm_map)
       else:
           svn_perm_map = {"repo": self.address,
                           "working_folder": self.working_copy}
           run("svn info https://%(repo)s <%(working_folder)s/svn_ans_t.txt"
                % svn_perm_map)


class Templates:

    def __init__(self, cfg):
        self.cfg = cfg
        utils = Utils()
        self.template_folder = utils.get_fab_path() + "/templates"

    def template(self, template_file, template_map):
        ftmpl = open("%s/%s" % (self.template_folder, template_file))
        fcontents = ftmpl.read()
        return fcontents % template_map

    def new_file(
        self,
        template_file,
        template_map,
        output_dir,
        ):
        contents = self.template(template_file, template_map)
        from posixpath import basename
        print "generating from template file ", template_file
        new_file = basename(template_file).rstrip(".tmpl")
        print "new file from template going to be created ", new_file
        fnewfile = open("%(out_dir)s/%(file.conf)s" % {"out_dir"
                        : output_dir, "file.conf": new_file}, "w")
        fnewfile.write(contents)
        fnewfile.close()
        print new_file, " was created in ", output_dir


class Services:

    """
    Start and stop bungeni related services using the Supervisord service manager
    """

    def __init__(self):
        self.cfg = BungeniConfigs()
        self.pycfg = PythonConfigs(self.cfg, "supervisor")
        self.supervisord = self.pycfg.python_home \
            + "/bin/supervisord"
        self.supervisorctl = self.pycfg.python_home \
            + "/bin/supervisorctl"
        self.service_map = {"supervisorctl": self.pycfg.python_home \
                                                + "/bin/supervisorctl",
                            "supervisorconf": self.cfg.supervisorconf}

    def start_service(self, service, mode = "ABORT_ON_ERROR"):
        service_map = self.service_map.copy()
        service_map["service"] = service
        output = run("%(supervisorctl)s -c %(supervisorconf)s start %(service)s"
            % service_map)
        if "ERROR" in output:
            if mode == "ABORT_ON_ERROR":
                abort("Unable to start service " + service)
            else:
                print("Unable to start service " + service)


    def stop_service(self, service, mode = "ABORT_ON_ERROR"):
        service_map = self.service_map.copy()
        service_map["service"] = service
        output = run("%(supervisorctl)s -c %(supervisorconf)s stop %(service)s"
            % service_map)
        if "ERROR" in output:
            if mode == "ABORT_ON_ERROR":
                abort("Unable to stop service: " + service ) 
            else:
                print("Unable to stop service: " + service )


    def start_monitor(self):
        service_map = self.service_map.copy()
        service_map.pop("supervisorctl")
        service_map["supervisord"] = self.supervisord
        output = run("%(supervisord)s -c %(supervisorconf)s" % service_map)
        if "ERROR" in output:
            abort("Unable to start monitor")
            

    def stop_monitor(self):
        output = run("%(supervisorctl)s -c %(supervisorconf)s shutdown"
            % self.service_map)
        if "ERROR" in output:
            print("Unable to stop monitor")




class Tasks:

    """
    Class used for general buildout tasks
    Used by bungeni, plone and portal buildout tasks
    """

    def __init__(
        self,
        cfg,
        repo,
        working_folder,
        ):
        """
        cfg - BungeniConfigs object
        repo - Address of svn repository
            working_folder - working folder for checkout and for running buildout
        """

        self.cfg = cfg
        self.scm = SCM(self.cfg.development_build, repo,
                       self.cfg.svn_user, self.cfg.svn_password,
                       working_folder)

    def src_checkout(self):
        """
        Checks out the source code from subversion 
        """

        run("mkdir -p %s" % self.scm.working_copy)
        self.scm.checkout()

    def src_update(self):
        """
        Update the source of the working copy
        """

        self.scm.update()

    def buildout(
        self,
        boprefix,
        boparam,
        boconfig,
        ):
        """
        Runs the buildout for the currently set working copy
        boprefix = any prefix paths, variables etc
            boparam = any buildout params e.g. -N
        boconfig =  buildout configuration file
        """

        # Check for the verbose flag
        if self.cfg.verbose == True:
            if "v" not in boparam:
                if boparam[:1] == "-":
                    boparam = boparam + "vvv"
                else:
                    boparam = "-vvv"

        with cd(self.scm.working_copy):
            run("%s ./bin/buildout -t 3600 %s -c %s" % (boprefix,
                boparam, boconfig))

    def build_exists(self, li_files):
        for file in li_files:
            if not os.path.exists(file):
                return False
        return True

    def get_buildout_index(self, boconfig):
        """    
        Returns the index being used by the buildout configuration file
        This is specificed in :
        [buildout]
            index = 
        """

        path_to_bo_config = "%(buildout_folder)s/%(buildout_config)s" \
            % {"buildout_folder": self.scm.working_copy,
               "buildout_config": boconfig}
        print " getting buildout index from ", path_to_bo_config
        buildout_config = SafeConfigParser()
        buildout_config.read("%(buildout_folder)s/%(buildout_config)s"
                             % {"buildout_folder"
                             : self.scm.working_copy, "buildout_config"
                             : boconfig})
        return buildout_config.get("buildout", "index")

    def check_versions(self, boprefix, boparam, boconfig):
        """
        Check the buildout version    
        """
        with cd(self.scm.working_copy):
            run("%s ./bin/buildout -t 3600  %s -c %s | sed -ne 's/^Picked: //p' | sort | uniq" % (boprefix, boparam, boconfig))

        """
        versions_file = self.scm.working_copy + '/versions.cfg'
        print 'boconfig = ', boconfig
        checkVer = checkversions.CheckVersions(versions_file,
                self.get_buildout_index(boconfig), py_ver)
        return checkVer.checkVersion()
        """

    def bootstrap(self, pythonexec):
        """
        Bootstraps a buildout
        Checks if bootstrap.py exists in the current folder, if not, uses the one from the parent folder
        """

        path_prefix = ""
        if os.path.isfile(self.scm.working_copy + "/bootstrap.py"):
            path_prefix = "./"
        else:
            path_prefix = "../"
        with cd(self.scm.working_copy):
            run("%s %sbootstrap.py" % (pythonexec, path_prefix))

    def local_config(
        self,
        template_file,
        template_map,
        bo_localconfig,
        ):
        if self.cfg.local_cache == True:
            templates = Templates(self.cfg)
            templates.new_file(template_file, template_map,
                               self.scm.working_copy)

    def update_ini(
        self,
        ini_file,
        section,
        option,
        value,
        ):
        deploy_cfg = SafeConfigParser()
        deploy_cfg.read(ini_file)
        deploy_cfg.set(section, option, value)
        deploy_cfg.write(open(ini_file, "w"))


class PloneTasks:

    def __init__(self):
        self.cfg = BungeniConfigs()
        self.pycfg = PythonConfigs(self.cfg, "plone")
        self.tasks = Tasks(self.cfg, self.cfg.plone_repo,
                           self.cfg.user_plone)
        self.exists_check = [self.cfg.user_bungeni,
                             self.cfg.user_bungeni + "/bin/paster",
                             self.cfg.postgresql_bin]
        if not self.tasks.build_exists(self.exists_check):
            abort(red("The Plone buildout requires an existing bungeni buildout"
                  ))

    def setup(self):
        self.tasks.src_checkout()
        self.tasks.bootstrap(self.pycfg.python)
        self.deploy_ini()

    def build(self):
       """
       Runs a full plone buildout
       """

       self.tasks.buildout("PATH=%s:$PATH PYTHON=%s"
                            % (self.cfg.postgresql_bin,
                            self.pycfg.python), "",
                            self.cfg.plone_buildout_config)

    def build_opt(self):
       """
       Runs a optimistic plone buildout
       """

       self.tasks.buildout("PATH=%s:$PATH PYTHON=%s"
                            % (self.cfg.postgresql_bin,
                            self.pycfg.python), "-N",
                            self.cfg.plone_buildout_config)

    def deploy_ini(self):
        run("cp %(plone)s/deploy.ini %(deploy_ini)s" % {"plone"
            : self.cfg.user_plone, "deploy_ini"
            : self.cfg.plone_deploy_ini})

    def check_versions(self):
       """
       Verifies packages in the plone version index
       """
       self.local_config()
       self.tasks.check_versions("PATH=%s:$PATH PYTHON=%s"
                           % (self.cfg.postgresql_bin,
                           self.pycfg.python), "-Novvvvv", self.cfg.plone_buildout_config)


    def local_config(self):
        template_map = {"plone_local_index": self.cfg.plone_local_index}
        template_file = "%(plone_local_cfg)s.tmpl" \
            % {"plone_local_cfg": self.cfg.plone_local_buildout_config}
        self.tasks.local_config(template_file, template_map,
                                self.cfg.plone_local_buildout_config)
        print "Local config ", self.cfg.plone_local_buildout_config, \
            " generated from ", template_file

    
    def import_site_content(self):
        with cd(self.cfg.user_plone):
            with cd("./parts/instance/import"):
                plone_site_content_file  = run("basename %s" % self.cfg.plone_site_content)
                run("if [ -f %(file)s ]; then rm %(file)s ; fi" % {"file":plone_site_content_file})
                run("if [ -f *.zexp ]; then rm *.zexp ; fi")
                run("wget %s" % self.cfg.plone_site_content)
                run("tar xvf %s" % plone_site_content_file)
            run("%(python)s import-data.py" % {"python":self.pycfg.python})


    def update_deployini(self):
        self.tasks.update_ini(self.cfg.plone_deploy_ini, "server:main",
                              "port", self.cfg.plone_http_port)
        
    def update(self):
       """
       Update the plone source
       """
       self.tasks.src_update()


class PortalTasks:

    def __init__(self):
        self.cfg = BungeniConfigs()
        self.pycfg = PythonConfigs(self.cfg, "portal")
        self.tasks = Tasks(self.cfg, self.cfg.portal_repo,
                           self.cfg.user_portal)
        self.exists_check = [self.cfg.user_bungeni,
                             self.cfg.user_bungeni + "/bin/paster"]
        if not self.tasks.build_exists(self.exists_check):
            abort("Portal build requires a working bungeni buildout")

    def setup(self):
        self.tasks.src_checkout()
        self.tasks.bootstrap(self.pycfg.python)
        self.deploy_ini()

    def build(self):
        self.local_config()
        self.tasks.buildout("PYTHON=%s" % self.pycfg.python, "",
                            self.cfg.portal_buildout_config)

    def build_opt(self):
        self.local_config()
        self.tasks.buildout("PYTHON=%s" % self.pycfg.python, "-N",
                            self.cfg.portal_buildout_config)

    def check_versions(self):
       """
       Verifies packages in the plone version index
       """
       self.local_config()
       self.tasks.check_versions("PYTHON=%s"
                           % self.pycfg.python, "-Novvvvv", self.cfg.portal_buildout_config)

    def deploy_ini(self):
        run("cp %(portal)s/deploy.ini %(deploy_ini)s" % {"portal"
            : self.cfg.user_portal, "deploy_ini"
            : self.cfg.portal_static_ini})

    def local_config(self):
        template_map = \
            {"portal_local_index": self.cfg.portal_local_index}
        template_file = "%(portal_local_cfg)s.tmpl" \
            % {"portal_local_cfg": self.cfg.portal_local_buildout_config}
        self.tasks.local_config(template_file, template_map,
                                self.cfg.portal_local_buildout_config)
        print "Local config ", self.cfg.portal_local_buildout_config, \
            " generated from ", template_file        

    def update_deployini(self):
        print "Updating portal static.ini"
        self.tasks.update_ini(self.cfg.portal_static_ini, "DEFAULT",
                              "static_port",
                              self.cfg.portal_static_port)
        self.update_deliverance_proxy_config()
        
        
    def update_deliverance_proxy_config(self):
        print "Updating portal deliverance-proxy.conf"
        theme_url = self.cfg.portal_web_server_port == "80" and\
                    self.cfg.portal_web_server_host or\
                    "%s:%s" % (self.cfg.portal_web_server_host, self.cfg.portal_web_server_port)                    
        if self.cfg.country_theme == "default":
            country_theme = ""
        else:
            country_theme = self.cfg.country_theme
        template_map = \
            {"app_host": self.cfg.app_host,
             "portal_http_port": self.cfg.portal_http_port,
             "portal_theme": self.cfg.portal_theme,
             "bungeni_http_port": self.cfg.bungeni_http_port,
             "plone_http_port": self.cfg.plone_http_port,
             "portal_static_port": self.cfg.portal_static_port,
             "web_server_host": self.cfg.portal_web_server_host,
             "web_server_port": self.cfg.portal_web_server_port,
             "theme_url": theme_url,
             "country_theme": country_theme}
        config_file_path = os.path.join(self.cfg.user_portal, "deliverance-proxy.conf")
        with open(config_file_path, "w") as config_file:
            tmpl = Templates(self.cfg)
            config_file.write(tmpl.template("deliverance-proxy.conf.tmpl", template_map))
        

    def update(self):
       """
       Update the portal
       """

       self.tasks.src_update()



class BungeniTasks:

    def __init__(self):
        self.cfg = BungeniConfigs()
        self.pycfg = PythonConfigs(self.cfg, "bungeni")
        self.data_dump_folder = self.cfg.user_bungeni + "/testdatadmp"
        self.data_dump_file = self.data_dump_folder + "/" \
            + self.cfg.bungeni_dump_file
        self.min_dump_file = self.data_dump_folder \
            + "/min-dump.txt"
        self.large_dump_file = self.data_dump_folder \
            + "/dmp_undesa_large.txt"
        self.tasks = Tasks(self.cfg, self.cfg.bungeni_repo,
                           self.cfg.user_bungeni)
        self.exists_check = [self.pycfg.python]
        if not self.tasks.build_exists(self.exists_check):
            abort("Bungeni build requires a working python " + self.pycfg.python_ver )

    def setup(self, version = "default"):
        self.tasks.src_checkout()
        if version == "HEAD":
            with cd(self.cfg.user_bungeni):
                with cd("src"):
                    run("svn up -rHEAD ./bungeni.main ./bungeni_custom")
        self.tasks.bootstrap(self.pycfg.python)
        self.install_bungeni_custom()
        self.deploy_ini()

    def deploy_ini(self):
        run("cp %(bungeni)s/deploy.ini %(deploy_ini)s" % {"bungeni"
            : self.cfg.user_bungeni, "deploy_ini"
            : self.cfg.bungeni_deploy_ini})

    def update(self, version = "default"):
       """
       Update the bungeni source folder
       """

       self.tasks.src_update()
       if version == "HEAD":
           with cd(self.cfg.user_bungeni):
               with cd("src"):
                   run("svn up -rHEAD ./bungeni.main ./bungeni_custom")

    def build(self):
       """
       Run a buildout of the bungeni installation
       """

       self.local_config()
       self.tasks.buildout("PATH=%s:$PATH PYTHON=%s"
                           % (self.cfg.postgresql_bin,
                           self.pycfg.python), "",
                           self.cfg.bungeni_buildout_config)

    def build_opt(self):
        self.local_config()
        self.tasks.buildout("PATH=%s:$PATH PYTHON=%s"
                            % (self.cfg.postgresql_bin,
                            self.pycfg.python), "-N",
                            self.cfg.bungeni_buildout_config)

    def check_versions(self):
        self.local_config()
        self.tasks.check_versions("PATH=%s:$PATH PYTHON=%s"
                            % (self.cfg.postgresql_bin,
                            self.pycfg.python), "-Novvvvv", self.cfg.bungeni_buildout_config)

    def reset_db(self):
        with cd(self.cfg.user_bungeni):
            run("./parts/postgresql/bin/dropdb bungeni")
            run("./parts/postgresql/bin/createdb bungeni")

    def reset_schema(self):
        with cd(self.cfg.user_bungeni):
            run("./bin/reset-db")

    def load_demo_data(self):
       """
       Updates the demo data for bungeni to use the current user name and then loads it into the db
       """

       with cd(self.cfg.user_bungeni):
           demo_dmp = self.__dump_update(self.data_dump_file)
           run("./bin/psql bungeni < %s"
                % demo_dmp)

    def dump_data(self, output_path):
        """
        Dumps the bungeni database data into a text file 
        """

        with cd(self.cfg.user_bungeni):
            run("./parts/postgresql/bin/pg_dump bungeni -a -O --disable-triggers > " + output_path)


    def restore_attachments(self):
        """
        Restores the attachments into the "fs" folder for the small data set
        """

        with cd(self.cfg.user_bungeni):
            run("mkdir -p %(attachments_folder)s" % \
                    {"attachments_folder":self.cfg.bungeni_attachments_folder} )
            with cd(self.cfg.bungeni_attachments_folder):
                run("tar --strip-components=2 -zvxf ../testdatadmp/%(attachments_archive)s" % \
                        {"attachments_archive":self.cfg.bungeni_attachments_archive})


    def load_min_data(self):
        with cd(self.cfg.user_bungeni):
            min_dump = self.__dump_update(self.min_dump_file)
            run("./bin/psql bungeni < %s" % min_dump)


    def load_large_data(self):
        with cd(self.cfg.user_bungeni + "/testdatadmp"):
             run("if [ -f %(large_dump)s ]; then rm %(large_dump)s ; fi" % {"large_dump":self.large_dump_file})
             large_file_gz = run("basename $(head -1 large.txt)")
             run("if [ -f  %s ]; then echo 'file exists'; else head -1 large.txt | xargs wget; fi")
             run("basename $(head -1 large.txt) | xargs tar xvf") 
             run("basename $(head -1 large.txt) | xargs rm")
             large_dump = self.__dump_update(self.large_dump_file)
             run("../bin/psql bungeni < %s" %  large_dump)


    def restore_large_attachments(self):
        """
        Restores large data dump attachments
        """
        large_att_gz = ""
        with cd(self.cfg.user_bungeni + "/testdatadmp"):
            large_att_url = run("tail -n 1 large.txt")
            large_att_gz = run("basename $(tail -n 1 large.txt)")
            run("if [ -f %(attachments_archive)s ]; then rm %(attachments_archive)s ; fi" % \
                    {"attachments_archive":large_att_gz})
            run("if [ -f  %(attachments_archive)s ]; then echo 'file exists'; else echo %(attachments_archive_url)s | xargs wget; fi" % \
                    {"attachments_archive":large_att_gz , "attachments_archive_url":large_att_url})
        with cd(self.cfg.user_bungeni):
            run("mkdir -p %(attachments_folder)s" % \
                    {"attachments_folder":self.cfg.bungeni_attachments_folder} )
            with cd(self.cfg.bungeni_attachments_folder):
                run("tar --strip-components=2 -zvxf ../testdatadmp/%s" % large_att_gz)
                run("rm ../testdatadmp/%s" % large_att_gz)


    def  __dump_update(self, dump_file):
        with cd(self.cfg.user_bungeni):
           dict_dump_update = {
                "db_dump_update_script": self.cfg.db_dump_update_script,
                "data_dump_file": dump_file,
                "output_file": self.data_dump_folder + "/dmp_upd.txt",
                "output_user": env["user"],
                }
           run("%(db_dump_update_script)s %(data_dump_file)s %(output_file)s undesa %(output_user)s" % dict_dump_update)
           return self.data_dump_folder + "/dmp_upd.txt"



    def local_config(self):
        template_map = {
            "bungeni_local_index": self.cfg.bungeni_local_index,
            "postgresql_local_url": self.cfg.postgresql_local_url,
            "xapian_local_url": self.cfg.xapian_local_url,
            "xapian_bindings_local_url": self.cfg.xapian_bindings_local_url,
            }
        template_file = "%(bungeni_local_cfg)s.tmpl" \
            % {"bungeni_local_cfg": self.cfg.bungeni_local_buildout_config}
        self.tasks.local_config(template_file, template_map,
                                self.cfg.bungeni_local_buildout_config)

    def setupdb(self):
       """
       Setup the postgresql db - this needs to be run just once for the lifetime of the installation
       """

       with cd(self.cfg.user_bungeni):
            run("./bin/setup-database")

    def update_deployini(self):
        self.tasks.update_ini(self.cfg.bungeni_deploy_ini, "server:main"
                              , "port", self.cfg.bungeni_http_port)

    def install_bungeni_custom(self):
        bungeni_custom_map = {
            "site_packages" : self.pycfg.python_packages ,
            "folder_bungeni_custom" : self.cfg.user_bungeni + "/src" ,
            "bungeni_custom" : self.cfg.bungeni_custom_pth,
            "user_bungeni": self.cfg.user_bungeni
            }
        ## delete an existing symlink
        run("cd %(user_bungeni)s && if [ -f %(bungeni_custom)s ]; then rm %(bungeni_custom)s ; fi"\
                % {"user_bungeni" : bungeni_custom_map["user_bungeni"], "bungeni_custom" : \
                    bungeni_custom_map["bungeni_custom"] })
        ## create a new .pth file in bungeni python site-packages
        run("cd %(site_packages)s && echo %(folder_bungeni_custom)s > %(bungeni_custom)s && "\
                "ln -s %(site_packages)s/%(bungeni_custom)s %(user_bungeni)s/" % bungeni_custom_map)

      
    def add_admin_user(self):
        """
        Adds the bungeni admin user based on the admin_user and admin_password entries 
        in setup.ini:bungeni
        """

        pass_map = {
            "user" : self.cfg.bungeni_admin_user,
            "pass" : self.cfg.bungeni_admin_password
           }
        with cd(self.cfg.user_bungeni):
            run("echo -e '%(user)s\n%(pass)s\n%(pass)s\n' > .pass.txt" % pass_map)
            run("./bin/admin-passwd < .pass.txt")
            run("rm .pass.txt")



class CustomTasks:
    
    def __init__(self):
        # do something here
        self.cfg = BungeniConfigs()


    def remap_custom(self):
        with cd(self.cfg.user_bungeni):
            run("mkdir -p %s" % self.cfg.custom_folder)
            run("cp -R ./src/bungeni_custom/* %s" % self.cfg.custom_folder)
            with cd(self.cfg.custom_folder):
                run("find . -name '*.svn' -print0 | xargs -0 rm -rf ")
            run("echo `pwd` > %s " % self.cfg.bungeni_custom_pth)

    def map_translations(self, switch):
        translations_path = ""
        if switch == "custom":
            translations_path = "/".join((self.cfg.user_bungeni,
                                         self.cfg.custom_folder,
                                         "translations"
                                        ))
        elif switch == "default":
            translations_path = "/".join((self.cfg.user_bungeni,
                                         "src",
                                         "bungeni_custom",
                                         "translations"
                                        ))
        else:
            print red("You need to specify translations target")
            return
        packages_home = "/".join((self.cfg.user_bungeni,
                                     "src",
                                     "bungeni.main"
                                    ))
        if not exists(translations_path):
            print red("Translations folder %s not found. Skipping installation."
            % translations_path)
            return
        else:
            for package in self.cfg.translatable_packages:
                for language in self.cfg.enabled_translations:
                    source_path = "%s/bungeni/%s/locales/%s"\
                    %(packages_home, package, language)
                    target_path = "%s/bungeni.%s/locales/%s"\
                    %(translations_path, package, language)
                    if exists(target_path):
                        if exists(source_path):
                            print red("Source path %s already exists" % source_path)
                        else:
                            run("ln -s %s %s" %(target_path, source_path))
                            print green("Linked %s translations for module %s"
                            % (language, package))
                    else:
                        print red("Translation target %s does not exist" % target_path)
            #unified translations
            for language in self.cfg.enabled_translations:
                print green("Setting up bungeni translations")
                source_path = "%s/bungeni/locales/%s"\
                    %(packages_home, language)
                target_path = "%s/bungeni/%s"\
                    %(translations_path, language)
                if exists(target_path):
                    if exists(source_path):
                        print red("Source path %s already exists" % source_path)
                    else:
                        run("ln -s %s %s" %(target_path, source_path))
                        print green("Linked %s translations"
                            % language)
                else:
                    print red("Translation target %s not found" % target_path)
            


    def map_country_theme(self):
        country_theme = self.cfg.country_theme 
        if country_theme != "default" and country_theme != "":
            source_path = os.path.join(os.path.dirname(self.cfg.user_bungeni),
                                       "bungeni/src/bungeni_custom/themes",
                                        country_theme)
            theme_path = os.path.join(os.path.dirname(self.cfg.user_bungeni),
                                      "bungeni/src/bungeni.main/bungeni/",
                                      "portal/static/themes",country_theme)
            if os.path.exists(source_path): 
                if os.path.exists(theme_path):                               
                    if os.path.islink(theme_path): 
                        run("unlink %s" %(theme_path))
                    else:
                        print red("Cannot enable '%s' theme. Another theme file " 
                        "already exists in the target folder." % country_theme)
                        return
                run("ln -s %s %s" %(source_path, theme_path))
                print green("Country theme '%s' enabled." % country_theme)
            else:
                print red("Country theme '%s' not found in custom folder." 
                          "Default theme used instead." % country_theme)
        else:
            print green("No country theme specified. Default theme used.")                                                 
