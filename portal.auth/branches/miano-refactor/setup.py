from setuptools import setup, find_packages

setup(
    name="portal.auth",
    version="0.1",
    author='Bungeni team',
    author_email='info@bungeni.org',
    description='Authentication module for Bungeni Portal',
    license="GPL",
    keywords = "zope3",
    classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
    packages=find_packages(),
    package_data = { '': ['*.txt', '*.zcml', '*.pt', '*.css', '*.gif', '*.png'] },
    namespace_packages=['portal'],
    install_requires = [ 'setuptools',
                         'repoze.who',
                         'zope.interface',
                         'zope.app.security',
                         'SQLAlchemy',
                         'WebOb'],
    zip_safe = False,
    )

