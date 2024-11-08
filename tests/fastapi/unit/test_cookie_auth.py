import http
from collections.abc import Callable

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import compose

app = FastAPI()


def cookie_auth() -> compose.fastapi.CookieAuth:
    return compose.fastapi.CookieAuth(name="token")


@app.get("/auth", dependencies=[Depends(cookie_auth())])
def authed():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "get_cookies, expected_status_code",
    [
        (
            lambda: {},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {"token": "token"},
            http.HTTPStatus.OK,
        ),
    ],
    ids=(
        "인증 쿠키 누락",
        "인증 쿠키 전달",
    ),
)
def test_auth(get_cookies: Callable[[], dict[str, str]], expected_status_code: int):
    response = client.get("/auth", cookies=get_cookies())

    assert response.status_code == expected_status_code
