# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2011 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt
import setuptools, os

dest = os.path.join(os.path.dirname(__file__),
                    'src', 'zdhtmlxscheduler', 'resources')
lbase = len(os.path.dirname(dest))+1
extpaths = []
for path, dirs, files in os.walk(dest):
    prefix = path[lbase:]
    for file in files:
        extpaths.append(os.path.join(prefix, file))
            
def read(*rnames):
    file_path = os.path.join(os.path.dirname(__file__), *rnames)
    return open( file_path ).read()

setuptools.setup(
    name = 'zdhtmlxscheduler',
    version = "1.0.3",
    author='Miano Njoka',
    author_email='miano@parliaments.info',
    description = "Zope3 Package of DHTMLX Scheduler",
    long_description=( read('README.txt')
                       + '\n\n' +
                       read('whatsnew.txt')
                       ),
    url='http://pypi.python.org/pypi/zdhtmlxscheduler',
    packages = setuptools.find_packages('src'),
    package_dir = {'':'src'},
    include_package_data = True,
    package_data = { '' : extpaths, 'zdhtmlxscheduler' : ["*.zcml"] },
    zip_safe=False,  
    install_requires = [
        'setuptools',
        'zc.resourcelibrary',
        ],
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],    
    )
