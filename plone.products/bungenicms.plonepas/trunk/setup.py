from setuptools import setup, find_packages

version = '0.1'

setup(name='bungenicms.plonepas',
      version=version,
      description="Bungeni SQLAlchemy PAS Plugins For Plone",
      keywords='plone pas sqlalchemy',
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      maintainer = 'Bungeni Developers',
      maintainer_email ='bungeni-dev@googlegroups.com',
      url='http://www.bungeni.org',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['bungenicms'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      )
