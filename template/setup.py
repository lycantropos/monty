from pathlib import Path

from setuptools import (find_packages,
                        setup)

import _project_

project_base_url = 'https://github.com/_github_login_/_project_/'

setup(name=_project_.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=_project_.__version__,
      description=_project_.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='_full_name_',
      author_email='_email_',
      classifiers=[
          '_license_classifier_',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],
      license='_license_',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      install_requires=Path('requirements.txt').read_text(encoding='utf-8'))
