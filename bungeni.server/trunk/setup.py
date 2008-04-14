from setuptools import setup, find_packages

setup(name='bungeni.server',
      version='0.2',
      description="server packaging, deployment, startup of bungeni server",
      long_description="",
      keywords='',
      author='Bungeni Developers',
      author_email='bungeni-dev@googlegroups.com',
      url='http://www.bungeni.org',
      license='GPL',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   ],

      packages=find_packages(),
      namespace_packages=['bungeni'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools',
                        'ZODB3',
                        'ZConfig',
                        'zdaemon',
                        'zope.publisher',
                        'zope.traversing',
                        'zope.app.wsgi>=3.4.0',
                        'zope.app.appsetup',
                        'zope.app.zcmlfiles',
                        # The following packages aren't needed from the
                        # beginning, but end up being used in most apps
                        'zope.annotation',
                        'zope.copypastemove',
                        'zope.formlib',
                        'zope.i18n',
                        'zope.app.authentication',
                        'zope.app.session',
                        'zope.app.intid',
                        'zope.app.keyreference',
                        'zope.app.catalog',
                        # The following packages are needed for functional
                        # tests only
                        'zope.testing',
                        'zope.app.testing',
                        'zope.app.securitypolicy',
                        'zope.sendmail',
                        'collective.singing==0.1dev-r62028',
                        ],
      entry_points = """
      [paste.app_factory]
      main = bungeni.server.startup:application_factory
      """
      )
