from pathlib import Path

from setuptools import (find_packages,
                        setup)

import __project__

project_base_url = 'https://github.com/__github_login__/__project__/'

setup_requires = [
    'pytest-runner>=4.2',
]
install_require = Path('requirements.txt').read_text()
tests_require = Path('requirements-tests.txt').read_text()

setup(name=__project__.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
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
      install_require=install_require,
      tests_require=tests_require)
