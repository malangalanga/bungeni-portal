from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='Products.groupworkspaces',
      version=version,
      description="Customization for the Group Workspaces",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope2 zope3 bungeni groupworkspaces',
      author='Bungeni Developers',
      author_email='bungeni-dev@goolgegroups.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bungenicms.policy',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
