__project__
===========

[![](https://travis-ci.org/__github_login__/__project__.svg?branch=master)](https://travis-ci.org/__github_login__/__project__ "Travis CI")
[![](https://ci.appveyor.com/api/projects/status/github/__github_login__/__project__?branch=master&svg=true)](https://ci.appveyor.com/project/__github_login__/__project__ "AppVeyor")
[![](https://codecov.io/gh/__github_login__/__project__/branch/master/graph/badge.svg)](https://codecov.io/gh/__github_login__/__project__ "Codecov")
[![](https://img.shields.io/github/license/__github_login__/__project__.svg)](https://github.com/__github_login__/__project__/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/__project__.svg)](https://badge.fury.io/py/__project__ "PyPI")

In what follows `python3` is an alias for `python3.5` or any later
version (`python3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions

```bash
python3 -m pip install --upgrade pip setuptools
```

### Release

Download and install the latest stable version from `PyPI` repository

```bash
python3 -m pip install --upgrade __project__
```

### Developer

Download and install the latest version from `GitHub` repository

```bash
git clone https://github.com/__github_login__/__project__.git
cd __project__
python3 setup.py install
```

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version

```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version

```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version

```bash
bump2version --dry-run --verbose release
```

Bump version

```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

#### Notes

To avoid inconsistency between branches and pull requests,
bumping version should be merged into `master` branch as separate pull
request.

Running tests
-------------

Plain

```bash
python3 setup.py test
```

Inside `Docker` container

```bash
docker-compose up
```

Bash script (e.g. can be used in `Git` hooks)

```bash
./run-tests.sh
```

PowerShell script (e.g. can be used in `Git` hooks)

```powershell
.\run-tests.ps1
```
