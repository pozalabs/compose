import http

import pytest
from fastapi import FastAPI
from fastapi.params import Depends
from starlette.testclient import TestClient

import compose


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()
    api_key_header = compose.fastapi.APIKeyHeader(api_key="api-key")

    @_app.get("/items", dependencies=[Depends(api_key_header)])
    def create_item():
        return [{"name": "item_1"}, {"name": "item_2"}]

    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "auth, expected_status_code",
    [
        (
            compose.httpx.HeaderAPIKeyAuth.single("api-key"),
            http.HTTPStatus.OK,
        ),
        (
            compose.httpx.HeaderAPIKeyAuth.single("invali-api-key"),
            http.HTTPStatus.UNAUTHORIZED,
        ),
    ],
    ids=(
        "올바른 API Key를 사용한 인증",
        "올바르지 않은 API Key를 사용한 인증",
    ),
)
def test_single_key_auth(
    app: FastAPI,
    client: TestClient,
    auth: compose.httpx.HeaderAPIKeyAuth,
    expected_status_code: int,
):
    response = client.get("/items", auth=auth)

    assert response.status_code == expected_status_code


def test_header_api_key_auth_missing(app: FastAPI, client: TestClient):
    response = client.get("/items")

    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
