from pathlib import Path

from setuptools import (find_packages,
                        setup)

import _project_

project_base_url = 'https://github.com/_github_login_/_project_/'

setup_requires = [
    'pytest-runner>=4.2',
]
install_requires = Path('requirements.txt').read_text()
tests_require = Path('requirements-tests.txt').read_text()

setup(name=_project_._name_,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=_project_._version_,
      description=_project_._doc_,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='_full_name_',
      author_email='_email_',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require)
