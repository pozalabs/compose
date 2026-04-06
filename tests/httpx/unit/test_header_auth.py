import http

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.params import Depends
from fastapi.security.api_key import APIKeyBase
from starlette.testclient import TestClient

import compose


class HeaderAuth(APIKeyBase):
    def __init__(
        self,
        *,
        secrets: dict[str, str],
        auto_error: bool = True,
        scheme_name: str | None = None,
        description: str | None = None,
    ):
        self.secrets = secrets
        self.auto_error = auto_error
        self.scheme_name = scheme_name
        self.description = description

    async def __call__(self, request: Request) -> dict[str, str] | None:
        exc = HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="Not authenticated",
        )

        secrets = {name: value for name, value in request.headers.items() if name in self.secrets}

        if secrets != self.secrets:
            if self.auto_error:
                raise exc
            else:
                return None

        return secrets


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()
    header_single_key_auth = HeaderAuth(secrets={"x-api-key": "api-key"})
    header_multi_keys_auth = HeaderAuth(
        secrets={"x-client-id": "client-id", "x-client-secret": "client-secret"}
    )

    @_app.get("/items/single-key-auth", dependencies=[Depends(header_single_key_auth)])
    def list_items_single_key_auth():
        return [{"name": "item_1"}, {"name": "item_2"}]

    @_app.get("/items/multi-keys-auth", dependencies=[Depends(header_multi_keys_auth)])
    def list_items_multi_keys_auth():
        return [{"name": "item_1"}, {"name": "item_2"}]

    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "endpoint, auth, expected_status_code",
    [
        (
            "/items/single-key-auth",
            compose.httpx.HeaderAuth.from_api_key("api-key"),
            http.HTTPStatus.OK,
        ),
        (
            "/items/single-key-auth",
            compose.httpx.HeaderAuth.from_api_key("invali-api-key"),
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            "/items/multi-keys-auth",
            compose.httpx.HeaderAuth(
                {"x-client-id": "client-id", "x-client-secret": "client-secret"}
            ),
            http.HTTPStatus.OK,
        ),
    ],
    ids=(
        "올바른 API Key를 사용한 인증",
        "올바르지 않은 API Key를 사용한 인증",
        "올바른 Multi Keys를 사용한 인증",
    ),
)
def test_single_key_auth(
    app: FastAPI,
    client: TestClient,
    endpoint: str,
    auth: compose.httpx.HeaderAuth,
    expected_status_code: int,
):
    response = client.get(endpoint, auth=auth)

    assert response.status_code == expected_status_code


def test_header_api_key_auth_missing(app: FastAPI, client: TestClient):
    response = client.get("/items/single-key-auth")

    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
