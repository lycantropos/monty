from setuptools import (setup,
                        find_packages)

import __project__
from __project__.config import PROJECT_NAME

project_base_url = 'https://github.com/__github_login__/__project__/'
setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version=__project__.__version__,
      description='Python project template.',
      author='__full_name__',
      author_email='__email__',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      setup_requires=['pytest-runner>=3.0'],
      tests_require=[
          'pydevd>=1.1.1',  # debugging
          'pytest>=3.2.5',
          'pytest-cov>=2.5.1',
          'hypothesis>=3.38.5',
      ])
