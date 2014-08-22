from setuptools import setup, find_packages

setup(
    name="bungenicms.workspaces",
    version="0.1",
    author='Bungeni Developers',
    author_email='bungeni-dev@googlegroups.com',
    description="Plone workspaces for bungeni principals.",
    keywords = "plone bungeni workspaces",
      classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Plone'],
    packages=find_packages(),
    package_data = { '': ['*.txt', '*.zcml'] },
    namespace_packages=['bungenicms'],
    install_requires = [
          'setuptools',
          'bungenicms.policy',
          "Products.Scrawl", 
          "bungenicms.repository",                           
        ],
    zip_safe = False,
    )
