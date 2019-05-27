from typing import Optional

import pytest
from hypothesis import given

from monty import monty
from tests import strategies


@given(strategies.dockerhub_logins,
       strategies.invalid_dockerhub_logins)
def test_load_dockerhub_user(dockerhub_login: str,
                             invalid_dockerhub_login: str) -> None:
    user = monty.load_dockerhub_user(dockerhub_login)

    assert user['username'] == dockerhub_login

    with pytest.raises(ValueError):
        monty.load_dockerhub_user(invalid_dockerhub_login)


@given(strategies.github_logins,
       strategies.github_access_tokens,
       strategies.invalid_github_logins)
def test_load_github_user(github_login: str,
                          github_access_token: Optional[str],
                          invalid_github_login: str) -> None:
    user = monty.load_github_user(github_login,
                                  access_token=github_access_token)

    assert user['login'] == github_login

    with pytest.raises(ValueError):
        monty.load_github_user(invalid_github_login,
                               access_token=github_access_token)
