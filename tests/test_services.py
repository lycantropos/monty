from typing import Optional

import pytest

from scripts.monty import (load_dockerhub_user,
                           load_github_user)


def test_load_dockerhub_user(dockerhub_login: str,
                             invalid_dockerhub_login: str) -> None:
    user = load_dockerhub_user(dockerhub_login)

    assert user['username'] == dockerhub_login

    with pytest.raises(ValueError):
        load_dockerhub_user(invalid_dockerhub_login)


def test_load_github_user(github_login: str,
                          github_access_token: Optional[str],
                          invalid_github_login: str) -> None:
    user = load_github_user(github_login,
                            access_token=github_access_token)

    assert user['login'] == github_login

    with pytest.raises(ValueError):
        load_github_user(invalid_github_login,
                         access_token=github_access_token)
