from http import HTTPStatus

import pytest
import requests.exceptions
from hypothesis import given

from monty import monty
from tests import strategies
from tests.utils import Secured


@given(strategies.dockerhub_logins)
def test_load_valid_dockerhub_user(dockerhub_login: str) -> None:
    user = monty.load_dockerhub_user(dockerhub_login)

    assert user['username'] == dockerhub_login


@given(strategies.invalid_dockerhub_logins)
def test_load_invalid_dockerhub_user(invalid_dockerhub_login: str) -> None:
    with pytest.raises(requests.exceptions.HTTPError) as error_ctx:
        monty.load_dockerhub_user(invalid_dockerhub_login)

    assert error_ctx.value.response.status_code == HTTPStatus.NOT_FOUND


@given(strategies.github_logins, strategies.github_access_tokens)
def test_load_valid_github_user(
    github_login: str, github_access_token: Secured
) -> None:
    user = monty.load_github_user(
        github_login, access_token=github_access_token.value
    )

    assert user['login'] == github_login


@given(strategies.github_access_tokens, strategies.invalid_github_logins)
def test_load_invalid_github_user(
    github_access_token: Secured, invalid_github_login: str
) -> None:
    with pytest.raises(requests.exceptions.HTTPError) as error_ctx:
        monty.load_github_user(
            invalid_github_login, access_token=github_access_token.value
        )

    assert error_ctx.value.response.status_code == HTTPStatus.FORBIDDEN
