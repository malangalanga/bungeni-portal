#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules import bungeni
from fabric.api import *
from fabric.context_managers import settings

def essentials():
    """
    Installs reqd OS packages as specified in distro.ini
    """

    bungenipre = bungeni.Presetup()
    bungenipre.essentials()


def build_python27():
    """
    Builds Python 2.7 from source
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_py27()


def build_python26():
    """
    Builds Python 2.6 from source
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_py26()


def build_imaging():
    """
    Build python imaging for active pythons
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_imaging()


def setup_pylibs():
    """
    Install setuptools, supervisor   Pythons(2.5,2.4)
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_imaging()
    bungenipre.required_pylibs()
    #bungenipre.install_appy()

def setup_setuptools():
    """
    Installs / Upgrades setuptools in the python installation
    """

    bungenipre = bungeni.Presetup()
    bungenipre.clear_ezsetup()
    bungenipre.setuptools()


def setup_docsplit():
    """
    Installs docsplit
    """
    
    bungenipre = bungeni.Presetup()
    bungenipre.docsplit_install()

    
def build_python():
    """
    Builds required pythons
    """
    
    cfg = bungeni.BungeniConfigs()
    pys = cfg.used_pythons()
    for py in pys:
        py_flat_name = py.replace(".","")
        # call the appropriate build_python26, build_python27 function
        globals()["build_python" + py_flat_name]()

def presetup():
    """
    Runs essentials, python installation (2.4,2.5) and reqd libs
    """
    
    essentials()
    build_python()
    postgres_install()
    rabbitmq_install()
    setup_pylibs() 
    setup_docsplit()
    varnish_install()


def bungeni_setup():
    """
    checkout & bootstrap bungeni source;setup bungeni_custom;generate deploy ini
    """

    tasks = bungeni.BungeniTasks()
    tasks.setup()


def bungeni_bootstrap():
    """
    Bootstrap the installation
    """

    tasks = bungeni.BungeniTasks()
    tasks.bootstrap_instance()


def bungeni_install():
    """
    Checkout,bootstrap and build bungeni
    Revision is based on the 'release' parameter in setup.ini
    """

    tasks = bungeni.BungeniTasks()
    # bootstrap
    tasks.setup()
    # do any local configuations
    tasks.local_config()
    # buildout 
    tasks.build()
    # setup-database
    tasks.setupdb()
    # switch bungeni custom
    switch_bungeni_custom()


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


def setup_bungeni_admin():
    """
    Setups the bungeni admin user
    """

    tasks = bungeni.BungeniTasks()
    tasks.add_admin_user()


def config_supervisord():
    """
    Generates the supervisor configuration
    """

    pre = bungeni.Presetup()
    pre.supervisord_config()
    pre.supervisor_docs()


def install_bungeni_custom():
    """
    Installs bungeni_custom into the bungeni python
    """

    tasks = bungeni.BungeniTasks()
    tasks.install_bungeni_custom()




def config_ini(which_ini):
    """
    Config deployment ini files : options (bungeni, plone, portal).
    Example: run ./fl config_ini:bungeni
    """

    tasks = None
    if which_ini == "bungeni":
        tasks = bungeni.BungeniTasks()
    elif which_ini == "plone":
        tasks = bungeni.PloneTasks()
    elif which_ini == "portal":
        tasks = bungeni.PortalTasks()
    else:
        abort("Nothing to do!option must be one of: bungeni, plone or portal")
        return
    tasks.deploy_ini()
    tasks.update_deployini()


def plone_install():
    """
    Setup and build plone
    Revision used is based on the 'release' parameter in setup.ini
    """

    tasks = bungeni.PloneTasks()
    tasks.setup()
    tasks.local_config()
    tasks.build()


def plone_import_site():
    """
    Import site content for Plone;This will overwrite existing content
    """

    tasks = bungeni.PloneTasks()
    tasks.import_site_content()


def plone_bootstrap():
    """
    Bootstrap the installation
    """

    tasks = bungeni.PloneTasks()
    tasks.bootstrap_instance()

            
def plone_setup():
    """
    Checkout and bootstrap plone
    """

    tasks = bungeni.PloneTasks()
    tasks.setup()


def plone_build():
    """
    Run the plone buildout
    """

    tasks = bungeni.PloneTasks()
    tasks.build()

def plone_build_opt():
    """
    Run the plone build optimistically (-N) 
    """

    tasks = bungeni.PloneTasks()
    tasks.build_opt()
    
def plone_build_minimal():
    """
    Run the plone build minimally: only workspaces installed. 
    """

    tasks = bungeni.PloneTasks()
    tasks.build_minimal()    


def plone_update():
    """
    Update the plone installation 
    """
    
    tasks = bungeni.PloneTasks()
    tasks.update()


def plone_conf():
    """
    Updates the zope.conf file for the plone installation
    """

    tasks = bungeni.PloneTasks()
    tasks.update_conf()

def plone_check():
    """
    Check the plone index for missing packages
    """

    tasks = bungeni.PloneTasks()
    __check(tasks)


def plone_local_config():
    """
    Generate local config for plone build
    """

    tasks = bungeni.PloneTasks()
    tasks.local_config()


def portal_install():
    """
    Setup and builds the portal
    Revision used is based on the 'release' parameter in setup.ini
    """

    tasks = bungeni.PortalTasks()
    tasks.setup()
    tasks.local_config()
    tasks.build()
    enable_demo_theme()


def portal_build():
    """
    Build the portal
    """

    tasks = bungeni.PortalTasks()
    tasks.build()


def portal_build_opt():
    """
    Build the portal with (-N)
    """

    tasks = bungeni.PortalTasks()
    tasks.build_opt()


def portal_bootstrap():
    """
    Bootstrap the installation
    """

    tasks = bungeni.PortalTasks()
    tasks.bootstrap_instance()


def portal_setup():
    """
    Checkout and bootstrap portal source
    """

    tasks = bungeni.PortalTasks()
    tasks.setup()


def __check(tasks):
    tasks.check_versions()


def portal_update():
    """
    Update the portal
    """
    tasks = bungeni.PortalTasks()
    tasks.update()


def portal_check():
    """
    Check missing packages for portal.buildout
    """

    tasks = bungeni.PortalTasks()
    __check(tasks)


def portal_local_config():
    """
    Generate a local buildout configuration.
    This is relevant only if you are using a local cache
    """

    tasks = bungeni.PortalTasks()
    tasks.local_config()


def bungeni_check():
    """
    Check missing packages for bungeni.buildout
    """

    tasks = bungeni.BungeniTasks()
    __check(tasks)


def start_service(*service_names):
    """
    Starts named services
    Example - to start bungeni: ./fl start_service:bungeni
              to start postgres rabbitmq and bungeni : ./fl start_service:postgres,rabbitmq,bungeni
    Other services are listed above (Supervisor status page)
    """

    service = bungeni.Services()
    for service_name in service_names:
        service.start_service(service_name)


def stop_service(*service_names):
    """
    Stops named services
    Example - to stop postgres: ./fl stop_service:postgres
              to stop postgres and bungeni: ./fl stop_service:postgres,bungeni
    Other services are listed above (Supervisor status page)
    """

    service = bungeni.Services()
    for service_name in service_names:
        service.stop_service(service_name)


def restart_service(*service_names):
    """
    Restarts services
    """ 
    
    stop_service(*service_names)
    start_service(*service_names)

def start_bungeni(mode="ABORT_ON_ERROR"):
    """
    Start bungeni
    """

    service = bungeni.Services()
    service.start_service("bungeni", mode)


def stop_bungeni(mode="ABORT_ON_ERROR"):
    """
    Stop bungeni
    """

    service = bungeni.Services()
    service.stop_service("bungeni", mode)


def start_serializer(mode="ABORT_ON_ERROR"):
    """
    Start bungeni
    """

    service = bungeni.Services()
    service.start_service("serializer", mode)


def stop_serializer(mode="ABORT_ON_ERROR"):
    """
    Stop bungeni
    """

    service = bungeni.Services()
    service.stop_service("serializer", mode)


def start_portal(mode="ABORT_ON_ERROR"):
    """
    Start the portal
    """

    service = bungeni.Services()
    service.start_service("portal", mode)


def stop_portal(mode="ABORT_ON_ERROR"):
    """
    Stop the portal
    """

    service = bungeni.Services()
    service.stop_service("portal", mode)


def start_plone(mode="ABORT_ON_ERROR"):
    """
    Start the plone service
    """

    service = bungeni.Services()
    service.start_service("plone", mode)


def stop_plone(mode="ABORT_ON_ERROR"):
    """
    Stop the plone service
    """

    service = bungeni.Services()
    service.stop_service("plone", mode)


#def start_postgres():
    #"""
    #Start postgres
    #"""

    #service = bungeni.Services()
    #service.start_service("postgres")

def start_exist(mode="ABORT_ON_ERROR"):
    """
    Start the eXist
    """

    service = bungeni.Services()
    service.start_service("exist", mode)


def stop_exist(mode="ABORT_ON_ERROR"):
    """
    Stop the eXist
    """

    service = bungeni.Services()
    service.stop_service("exist", mode)

def start_rabbitmq(mode="ABORT_ON_ERROR"):
    """
    Start the RabbitMQ
    """

    service = bungeni.Services()
    service.start_service("rabbitmq", mode)

def stop_rabbitmq(mode="ABORT_ON_ERROR"):
    """
    Stop the eXist
    """

    service = bungeni.Services()
    service.stop_service("rabbitmq", mode)
    
def start_varnish(mode="ABORT_ON_ERROR"):
    """
    Start varnish
    """

    service = bungeni.Services()
    service.start_service("varnish", mode)

def stop_varnish(mode="ABORT_ON_ERROR"):
    """
    Stop varnish
    """

    service = bungeni.Services()
    service.stop_service("varnish", mode)

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


def __db_load_services_stop():
    """
    Stop services - called before loading/resetting db
    """
    stop_bungeni("IGNORE_ERROR")
    stop_serializer("IGNORE_ERROR")
    stop_portal("IGNORE_ERROR")
    stop_plone("IGNORE_ERROR")


def __db_load_services_start():
    """
    Start services - called after loading/resetting db
    """
    start_bungeni("IGNORE_ERROR")
    start_serializer("IGNORE_ERROR")
    start_portal("IGNORE_ERROR")
    start_plone("IGNORE_ERROR")


def db_dump_data(to_path):
    """
    Dumps the bungeni db data
    Example: ./fl db_dump_data:/home/undesa/db-dump.txt
    """

    tasks = bungeni.BungeniTasks()
    tasks.dump_data(to_path)


def db_load_demodata():
    """
    Load demo data from the testdatadmp folder
    """

    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_schema()
    tasks.load_demo_data()
    tasks.restore_attachments()
    __db_load_services_start()


def db_load_mindata():
    """
    Load minimal data from the testdatadmp folder
    """

    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_schema()
    tasks.load_min_data()
    tasks.reset_attachments()
    __db_load_services_start()


def db_make_empty():
    """
    Make the bungeni db blank
    """

    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_db()
    __db_load_services_start()



def switch_bungeni_custom():
    """
    Makes a customized copy of bungeni_custom and makes it the active package
    """

    tasks = bungeni.CustomTasks()
    tasks.switch_bungeni_custom()

def restore_bungeni_custom():
    
    tasks = bungeni.BungeniTasks()
    tasks.install_bungeni_custom()


def enable_demo_theme():
    """
    Set demo theme, based on setup.ini parameter
    Parameter should map to a theme folder in portal.country_themes
    """
    tasks = bungeni.CustomTasks()
    tasks.enable_demo_theme()


def translate_workflow_xml(default_lang="en"):
    """
    Generates a translated workflow XML file. WARNING: RUN THIS ONLY IF YOU 
    KNOW WHAT THIS IS ABOUT
    """

    tasks = bungeni.CustomTasks()
    tasks.translate_workflow_xml(default_lang)


def exist_install():
   """
   Installs eXist, WARNING: Will overwrite any existing installation
   """    
   stop_exist("IGNORE_ERROR")
   tasks = bungeni.XmldbTasks()
   tasks.setup_exist()

def exist_fw_install():
    """
    Installs Bungeni eXist framework, WARNING: Will overwrite any existing installation
    """
    start_exist("IGNORE_ERROR")
    import time
    time.sleep(5)
    tasks = bungeni.XmldbTasks()
    tasks.download_fw()
    tasks.ant_prop_config()
    tasks.ant_fw_setup_config()
    tasks.ant_indexes_install()
    tasks.ant_fw_install()
    gluetasks = bungeni.GlueScriptTasks()
    gluetasks.setup_i18n_catalogues()

def exist_load_demodata():
    """
    Loads demodata from the eXist repository
    """
    start_exist("IGNORE_ERROR")
    import time
    time.sleep(5)
    tasks = bungeni.XmldbTasks()
    tasks.setup_exist_demo_data()
    tasks.ant_demo_setup_config()
    tasks.ant_demo_install()

def exist_dump_data(to_path):
    """
    Dumps the eXits-db data
    Example: ./fl exist_dump_data:/home/undesa/on_db_r10186.tar.gz
    """

    xmldbtasks = bungeni.XmldbTasks()
    xmldbtasks.dump_data(to_path)

def exist_load_i18n():
    """
    Loads i18n catalogues retrieved from Bungeni .po files
    """
    start_exist("IGNORE_ERROR")
    import time
    time.sleep(5)
    gluetasks = bungeni.GlueScriptTasks()
    gluetasks.setup_i18n_catalogues()

def exist_reset():
    """
    Reset data in eXist repository
    """
    start_exist("IGNORE_ERROR")
    import time
    time.sleep(5)
    tasks = bungeni.XmldbTasks()
    tasks.ant_prop_config()
    tasks.ant_demo_reset_config()
    tasks.ant_demo_reset()

def ant_version():
    """
    Get the Ant version used by eXist
    """
    tasks = bungeni.XmldbTasks()
    tasks.ant_version()
    
    
def ant_run(buildfile="build.xml"):
    """
    Run the Ant Script provided as the parameter
    """
    tasks = bungeni.XmldbTasks()
    tasks.ant_run(buildfile)

def rabbitmq_install():
    """
    Installs RabbitMQ, WARNING: Will overwrite any existing installation
    """
    #stop_rabbitmq("IGNORE_ERROR")
    tasks = bungeni.RabbitMQTasks()
    tasks.setup_rabbitmq()

def rabbitmq_reset():
    """
    Purges all queues created for Bungeni.
    """
    tasks = bungeni.RabbitMQTasks()
    tasks.rabbitmq_purge()

def rabbitmq_switch_admin():
    """
    Run this only if your rabbitmq is using the default guest user as admin. This action will switch it to use the admin info specified in setup.ini
    """
    tasks = bungeni.RabbitMQTasks()
    tasks.add_admin()


def jython_install():
    """
    Install/Reinstall jython
    """    
    tasks = bungeni.GlueScriptTasks()
    tasks.setup_jython()
    tasks.setup_jython_libs()


def glue_install():
    """
    Installs Jython, WARNING: Will overwrite any existing installation
    """
    tasks = bungeni.GlueScriptTasks()
    tasks.setup_jython()
    tasks.setup_jython_libs()
    tasks.setup_glue()
    tasks.glue_setup_config()

def glue_update():
    """
    Updates the glue source-code only - ignores jython and other libs.
    """
    tasks = bungeni.GlueScriptTasks()
    tasks.setup_glue()
    tasks.glue_setup_config()

def glue_reset():
    """
    Reset glue - to be run between fresh selenium runs 
    """
    tasks = bungeni.GlueScriptTasks()
    tasks.reset()


def config_glue():
    """
    Generates glue_script configuration
    """
    tasks = bungeni.GlueScriptTasks()
    tasks.glue_setup_config()

def exist_stack_update():
    """
    Updates eXist framework and glue-script files
    """
    exist_fw_install()
    gtasks = bungeni.GlueScriptTasks()
    gtasks.setup_glue()
    gtasks.glue_setup_config()

def exist_presetup():
    """
    Installs RabbitMQ / eXist dependencies
    """
    bungenipre = bungeni.Presetup()
    bungenipre.exist_essentials()
    bungenipre.pika()
    bungenipre.magic()
    bungenipre.pyinotify()

def exist_java_home():
    """
    Prints out the install location of the Java used by eXist
    """
    cfgs = bungeni.BungeniConfigs()
    print cfgs.java_home
    
def postgres_install():
    """
    Build and install postgres
    """
    postgres = bungeni.PostgresTasks()
    postgres.build_postgres()
    
def varnish_install():
    """
    Build and install varnish HTTP accelerator
    """
    varnish = bungeni.VarnishTasks()
    varnish.setup_varnish()
    varnish.create_vlc_file()
    
def config_varnish():
    """
    Generates the varnish configuration file (VCL)
    """
    varnish = bungeni.VarnishTasks()
    varnish.varnish_config()
    
def varnish_warmup():
    """
    Warmup the varnish cache
    """
    varnish = bungeni.VarnishTasks()
    varnish.varnish_warmup_cache()
    
def varnish_purge():
    """
    Warmup the varnish cache
    """
    varnish = bungeni.VarnishTasks()
    varnish.varnish_purge_cache()

	
def reset_all():
    """
    Resets Bungeni, eXist XML db and the message queue
    """
    # RabbitMQ is reset first to prevent the bungeni serialization thread from crashing
    with settings(warn_only=True):
        rabbitmq_reset()
        db_load_mindata()
        exist_reset()
        glue_reset()


def install_config_editor():
    """
    Install Bungeni ConfigEditor on eXist-db
    """
    tasks = bungeni.XmldbTasks()
    tasks.download_ce()
    tasks.ant_prop_config()
    tasks.ant_ce_setup_config()
    tasks.ant_ce_install()


def clear_logs():
    """
    Clears log files in the logs folder
    """
    service = bungeni.Services()
    service.clear_logs() 
