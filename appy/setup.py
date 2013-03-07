#!/usr/bin/env python
"""
Egg setup file for appy 0.7.0
 * put the setup.py in a folder, 
 * create a folder called src
 * within src extract the appy package zip file
 * run : python setup.py bdist_egg
"""

from setuptools import setup

setup(name='appy',
      version='0.8.3',
      description='Appy (Applications in python) is a bunch of tools distributed under the GPL license',
      include_package_data=True,
      author='Gaetan Delannay',
      author_email='ashok@parliaments.info',
      url='https://launchpad.net/appy',
      packages=['appy'],
      package_dir={'appy':'src/appy'},
      package_data={'appy':[
            #'gen/odt/templates/basic.odt', 
            'shared/*.py', 
            'shared/data/*.py', 
            'shared/data/*.txt', 
            'pod/*.py', 
            'pod/*.xml', 
            'pod/*.jpg', 
            'pod/test/*.*', 
            'pod/test/results/*.*',
            'pod/test/images/*.*',
            'pod/test/templates/*.*',
	]},
     )
