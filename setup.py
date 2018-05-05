import os
from setuptools import setup

project_base_url = 'https://github.com/lycantropos/monty/'

setup_requires = [
    'pytest-runner>=3.0',
]
install_requires = [
    'click>=6.7',  # command-line interface
    'PyYAML>=3.12',  # loading settings
    'requests>=2.8.14',  # synchronous HTTP
]
tests_require = [
    'pydevd>=1.1.1',  # debugging
    'pytest>=3.2.1',
    'pytest-cov>=2.5.1',
    'hypothesis>=3.38.5',
]

setup(name='montemplate',
      scripts=[os.path.join('scripts', 'monty.py')],
      version='0.0.1',
      description='Python project generator.',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require)
