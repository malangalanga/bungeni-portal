from setuptools import setup, find_packages

setup(
    name="bungenicms.theme",
    version="0.1",
    author='Bungeni Developers',
    author_email='bungeni-dev@googlegroups.com',
    description="Portal integration using Deliverance.",
    keywords = "plone bungeni theme",
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
        ],
    zip_safe = False,
    )

