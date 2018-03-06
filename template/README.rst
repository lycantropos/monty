__project__
===========

|travis| |codecov| |license| |pypi|

In what follows ``python3`` is an alias for ``python3.5`` or any later
version (``python3.6`` and so on).

Installation
------------

Install the latest ``pip`` & ``setuptools`` packages versions

.. code:: bash

    python3 -m pip install --upgrade pip setuptools

Release
~~~~~~~

Download and install the latest stable version from ``PyPI`` repository

.. code:: bash

    python3 -m pip install --upgrade __project__

Developer
~~~~~~~~~

Download and install the latest version from ``GitHub`` repository

.. code:: bash

    git clone https://github.com/__github_login__/__project__.git
    cd __project__
    python3 setup.py install

Bumping version
---------------

Install `bumpversion`_.

Choose which version number category to bump following `semver
specification`_.

Test bumping version

.. code:: bash

    bumpversion --dry-run --verbose $VERSION

where ``$VERSION`` is the target version number category name, possible
values are ``patch``/``minor``/``major``.

Bump version

.. code:: bash

    bumpversion --verbose $VERSION

**Note**: to avoid inconsistency between branches and pull requests,
bumping version should be merged into ``master`` branch as separate pull
request.

Running tests
-------------

Plain

.. code:: bash

    python3 setup.py test

Inside ``Docker`` container

.. code:: bash

    docker-compose up

Inside ``Docker`` container with remote debugger

.. code:: bash

    ./set-dockerhost.sh docker-compose up

Bash script (e.g. can be used in ``Git`` hooks)

.. code:: bash

    ./run-tests.sh

.. _bumpversion: https://github.com/peritus/bumpversion#installation
.. _semver specification: http://semver.org/

.. |travis| image:: https://travis-ci.org/__github_login__/__project__.svg?branch=master
   :target: https://travis-ci.org/__github_login__/__project__
.. |codecov| image:: https://codecov.io/gh/__github_login__/__project__/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/__github_login__/__project__
.. |license| image:: https://img.shields.io/github/license/__github_login__/__project__.svg
   :target: https://github.com/__github_login__/__project__/blob/master/LICENSE
.. |pypi| image:: https://badge.fury.io/py/__project__.svg
   :target: https://badge.fury.io/py/__project__
