import os
from typing import Optional

import pytest

from tests import strategies
from tests.utils import example


@pytest.fixture(scope='function')
def dockerhub_login() -> str:
    return example(strategies.dockerhub_logins)


@pytest.fixture(scope='function')
def github_login() -> str:
    return example(strategies.github_logins)


@pytest.fixture(scope='session')
def github_access_token() -> Optional[str]:
    return os.getenv('GITHUB_ACCESS_TOKEN')


@pytest.fixture(scope='function')
def invalid_dockerhub_login() -> str:
    return example(strategies.invalid_dockerhub_logins)


@pytest.fixture(scope='function')
def invalid_github_login() -> str:
    return example(strategies.invalid_github_logins)
