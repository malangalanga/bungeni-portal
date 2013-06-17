from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'bungenicms', 'publisher', 'version.txt')).read().strip()

setup(name='bungenicms.publisher',
    version=version,
    description="Publishes content types to production site.",
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
    author_email='info@parliments.info',
    url='http://www.parliaments.info/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bungenicms'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      # -*- Extra requirements: -*-
      ],
    extras_require={
        'sender': [
            'ftw.publisher.sender'
            ],
        'receiver': [
            'ftw.publisher.receiver'
            ],
        },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
    )
