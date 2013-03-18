from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'bungenicms', 'membershipdirectory', 'version.txt')).read().strip()

setup(name='bungenicms.membershipdirectory',
    version=version,
    description="A directory of member profiles",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='',
    author='UNDESA',
    author_email='info@parliaments.info',
    url='http://www.parliaments.info/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bungenicms'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      'Products.MasterSelectWidget',
      # -*- Extra requirements: -*-
      ],
    entry_points="""
      # -*- Entry points: -*-
      """,
    )
