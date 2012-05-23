from setuptools import setup, find_packages

setup(
    name="portal.theme",
    version="0.1",
    author='Bungeni team',
    author_email='info@bungeni.org',
    description='Default theme for Bungeni Portal',
    license="GPL",
    keywords = "deliverance",
    classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Deliverance'],
    packages=find_packages(),
    package_data = { '': ['*.txt','*.css', '*.gif', '*.png'] },
    namespace_packages=['portal'],
    install_requires = [ 'setuptools',
                         'Deliverance',
                         'pyquery'],
    zip_safe = False,
      entry_points =
    {
    'paste.app_factory' : [
        'static = portal.theme.app:make_static_serving_app'
        ],
    'paste.filter_app_factory' : [
        'deliverance = portal.theme.middleware:make_deliverance_middleware'
        ]
    }    
    )

