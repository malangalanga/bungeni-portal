#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules import bungeni
from fabric.api import *


def essentials():
    """
    Installs reqd OS packages as specified in distro.ini
    """

    bungenipre = bungeni.Presetup()
    bungenipre.essentials()


def build_python26():
    """
    Builds Python 2.6 from source
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_py26()


def build_python25():
    """
    Builds Python 2.5 from source
    """

    bungenipre = bungeni.Presetup()
    bungenipre.build_py25()


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


def build_python():
    """
    Builds required pythons
    """
    
    cfg = bungeni.BungeniConfigs()
    pys = []
    pys.append(cfg.cfg.get_config("bungeni","python"))
    pys.append(cfg.cfg.get_config("portal","python"))
    pys.append(cfg.cfg.get_config("plone","python"))
    pys.append(cfg.cfg.get_config("supervisor","python"))
    used_pys = set(pys)
    if "2.4" in used_pys:
        print "building python 2.4"
        build_python24()
    if "2.5" in used_pys:
        print "building python 2.5"
        build_python25()
    if "2.6" in used_pys:
        print "building python 2.6"
        build_python26()


def presetup():
    """
    Runs essentials, python installation (2.4,2.5) and reqd libs
    """
    
    essentials()
    build_python()
    setup_pylibs() 
    

def bungeni_setup():
    """
    checkout & bootstrap bungeni source;setup bungeni_custom;generate deploy ini
    """

    tasks = bungeni.BungeniTasks()
    tasks.setup()


def bungeni_install():
    """
    Checkout,bootstrap and build bungeni
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
    # install default po files
    install_translations("default")


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

def setup_bungeni_custom():
    """
    Installs the bungeni_custom library into the bungeni python site-packages folder
    """

    tasks = bungeni.BungeniTasks()
    tasks.install_bungeni_custom()


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


def install_bungeni_custom():
    """
    Installs bungeni_custom into the bungeni python
    """

    tasks = bungeni.BungeniTasks()
    tasks.install_bungeni_custom()




def config_ini(which_ini):
    """
    Config deployment ini files : bungeni, plone, portal
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
    """

    tasks = bungeni.PortalTasks()
    tasks.setup()
    tasks.local_config()
    tasks.build()


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


def start_service(service_name):
    """
    Starts a named service
    """

    service = bungeni.Services()
    service.start_service(service_name)


def stop_service(service_name):
    """
    Stops a named service
    """

    service = bungeni.Services()
    service.stop_service(service_name)


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


def start_plone():
    """
    Start the plone service
    """

    service = bungeni.Services()
    service.start_service("plone")


def stop_plone():
    """
    Stop the plone service
    """

    service = bungeni.Services()
    service.stop_service("plone")


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


def __db_load_services_stop():
    """
    Stop services - called before loading/resetting db
    """
    stop_bungeni()
    stop_portal()
    stop_plone()


def __db_load_services_start():
    """
    Start services - called after loading/resetting db
    """
    start_bungeni()
    start_portal()
    start_plone()


def db_load_demodata():
    """
    Load demo data from the testdatadmp folder
    """

    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_db()
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
    __db_load_services_start()


def db_load_largedata():
    """
    Load large metadata
    """
    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_db()
    tasks.load_large_data()
    tasks.restore_large_attachments()
    __db_load_services_start()


def db_make_empty():
    """
    Make the bungeni db blank
    """

    __db_load_services_stop()
    tasks = bungeni.BungeniTasks()
    tasks.reset_db()
    __db_load_services_start()



def remap_custom():
    """
    Remap custom
    """

    tasks = bungeni.CustomTasks()
    tasks.remap_custom()


def install_translations(switch="default"):
    """
    Links translations to custom source directory
    Call with "default" to use shipped translations or "custom"
    to use custom translations
    """
    tasks = bungeni.CustomTasks()
    tasks.map_translations(switch)

