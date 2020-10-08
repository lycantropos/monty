from pathlib import Path

from setuptools import (find_packages,
                        setup)

import {{project}}

project_base_url = 'https://github.com/{{github_login}}/{{project}}/'

setup(name={{project}}.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version={{project}}.__version__,
      description={{project}}.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='{{full_name}}',
      author_email='{{email}}',
      classifiers=[
          '{{license_classifier}}',
{% for minor in range(min_python_version.split(".")[1]|int, (max_python_version.split(".")[1])|int + 1) %}
          'Programming Language :: Python :: 3.{{minor}}',
{% endfor %}
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],
      license='{{license}}',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>={{min_python_version}}',
      install_requires=Path('requirements.txt').read_text(encoding='utf-8'))
