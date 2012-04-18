# Copyright (C) 2011 - UNDESA <www.parliaments.info>
#
# Author - Miano Njoka <miano@parliaments.info>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301  USA
import os, setuptools, shutil, urllib2, zipfile

package_url = "https://github.com/downloads/tinymce/tinymce/tinymce_3.5b3.zip"
package_name = "tinymce_3.5b3.zip"
prefix="tinymce/jscripts/tiny_mce/"

dest = os.path.join(os.path.dirname(__file__),
                    'src', 'z3tinymce', 'resources')
                            
extpaths = []
if not os.path.exists(dest):
    if not os.path.exists(package_name):
        x = urllib2.urlopen( package_url ).read()
        open(package_name, 'w').write(x)

    zfile = zipfile.ZipFile(package_name, 'r')
    lprefix = len(prefix)-1

    for file_name in sorted(zfile.namelist()):
        if file_name.startswith(prefix):
            file_name_part = file_name[lprefix:]
            destination_name = dest + file_name_part
            if destination_name[-1:] == '/':
                os.makedirs(destination_name)
            else:
                open(destination_name, 'w').write(zfile.read(file_name))
                extpaths.append(destination_name[lprefix:])
else:
    lbase = len(os.path.dirname(dest))+1
    for path, dirs, files in os.walk(dest):
        prefix = path[lbase:]
        for file in files:
            extpaths.append(os.path.join(prefix, file))

setuptools.setup(
    name = 'z3tinymce',
    version = 0.9,
    author='Miano Njoka',
    author_email='miano@parliaments.info',
    description = "Zope3 Package of TinyMCE",
    url='http://pypi.python.org/pypi/z3tinymce',
    packages = setuptools.find_packages('src'),
    package_dir = {'':'src'},
    include_package_data = True,
    zip_safe=False,
    package_data = {'z3tinymce': extpaths},    
    install_requires = [
        'setuptools',
        'zope.viewlet',
        'zc.resourcelibrary',
        'zope.interface',
        'zope.configuration'
        ],
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],    
    )
