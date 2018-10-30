from pathlib import Path

import __project__
from setuptools import (find_packages,
                        setup)

project_base_url = 'https://github.com/__github_login__/__project__/'

setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = [
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=3.73.1',
]

setup(name='__project__',
      packages=find_packages(exclude=('tests',)),
      version=__project__.__version__,
      description=__project__.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='__full_name__',
      author_email='__email__',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      tests_require=tests_require)
