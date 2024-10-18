import http
from collections.abc import Callable

import pendulum
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

import compose

app = FastAPI()


def jwt_issuer() -> compose.auth.JWTIssuer:
    return compose.auth.JWTIssuer.default(
        secret_key="secret-key",
        issuer="compose",
    )


def jwt_cookie_auth() -> compose.fastapi.JWTCookieAuth:
    return compose.fastapi.JWTCookieAuth(
        key="token",
        token_decoder=compose.auth.JWTDecoder(
            secret_key="secret-key",
            clock=pendulum.DateTime,
        ),
        on_token_lookup_error=lambda: HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
        on_token_decoding_error=lambda: HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )


@app.get("/auth", dependencies=[Depends(jwt_cookie_auth())])
def authed():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "get_cookies, expected_status_code",
    [
        (
            lambda: {"token": "wrong-token"},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {"token": jwt_issuer().issue(sub="id", expires_in=60)},
            http.HTTPStatus.OK,
        ),
    ],
    ids=(
        "올바르지 않은 토큰",
        "인증 쿠키 누락",
        "올바른 인증 쿠키",
    ),
)
def test_auth(get_cookies: Callable[[], dict[str, str]], expected_status_code: int):
    response = client.get("/auth", cookies=get_cookies())

    assert response.status_code == expected_status_code
