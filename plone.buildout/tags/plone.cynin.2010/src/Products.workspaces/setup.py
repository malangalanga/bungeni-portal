from setuptools import setup, find_packages
import sys, os

setup(name='Products.workspaces',
      version="0.1",
      description="Customization for group and member workspaces",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope2 zope3 bungeni workspaces',
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
