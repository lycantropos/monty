from setuptools import (setup,
                        find_packages)

import __project__
from __project__.config import PROJECT_NAME

project_base_url = 'https://github.com/__github_login__/__project__/'

setup_requires = [
    'pytest-runner>=3.0'
]
tests_require = [
    'pydevd>=1.1.1',  # debugging
    'pytest>=3.3.0',
    'pytest-cov>=2.5.1',
    'hypothesis>=3.38.5',
]

setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version=__project__.__version__,
      description=__project__.__doc__,
      long_description=open('README.md').read(),
      author='__full_name__',
      author_email='__email__',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      setup_requires=setup_requires,
      tests_require=tests_require)
