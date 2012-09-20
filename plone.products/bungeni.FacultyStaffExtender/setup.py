import os
from setuptools import setup
from setuptools import find_packages

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'bungeni', 'FacultyStaffExtender', 'version.txt')).read().strip()
    
shortdesc = 'Product to customize Products.FacultyStaffDirectory'
readme = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read() + "\n" + open(os.path.join(os.path.dirname(__file__), 'HISTORY.txt')).read()

setup(name='bungeni.FacultyStaffExtender',
      version=version,
      description=shortdesc,
      long_description=readme,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone widget',
      author='UNDESA',
      author_email='info@parliaments.info',
      url='http://www.parliaments.info/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bungeni'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'Products.FacultyStaffDirectory>=3.1',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
