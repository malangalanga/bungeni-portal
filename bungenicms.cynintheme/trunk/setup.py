from setuptools import setup, find_packages

version = '0.1'

setup(name='bungenicms.cynintheme',
      version=version,
      description="Cynin theme customizations for Bungeni.",
      long_description="""\
""",
      classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Plone'],
      keywords='"bungeni cynin theme"',
      author='Bungeni Developers',
      author_email='bungeni-dev@googlegroups.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bungenicms'],      
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',        
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
