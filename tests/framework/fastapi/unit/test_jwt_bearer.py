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


def jwt_bearer() -> compose.fastapi.JWTBearer:
    return compose.fastapi.JWTBearer(
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


@app.get("/auth", dependencies=[Depends(jwt_bearer())])
def authed():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "get_headers, expected_status_code",
    [
        (
            lambda: {"Authorization": "Bearer wrong-token"},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {"Authorization": f"Bearer {jwt_issuer().issue(sub="id", expires_in=60)}"},
            http.HTTPStatus.OK,
        ),
    ],
    ids=(
        "올바르지 않은 토큰",
        "인증 헤더 누락",
        "올바른 인증 헤더",
    ),
)
def test_auth(get_headers: Callable[[], dict[str, str]], expected_status_code: int):
    response = client.get("/auth", headers=get_headers())

    assert response.status_code == expected_status_code
