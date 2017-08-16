from setuptools import (setup,
                        find_packages)

from monty.config import PROJECT_NAME

project_base_url = 'https://github.com/lycantropos/monty/'
setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version='0.0.0',
      description='Python project skeleton.',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.tar.gz',
      setup_requires=['pytest-runner>=2.11'],
      tests_require=[
          'pydevd>=1.0.0',  # debugging
          'pytest>=3.0.5',
          'pytest-cov>=2.4.0',
          'hypothesis>=3.13.0',
      ])
