import http
from typing import Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import compose

app = FastAPI()
api_key_header = compose.fastapi.APIKeyHeader(api_key="api-key")


@app.get("/auth", dependencies=[Depends(api_key_header)])
def authed_by_api_key():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "headers, expected_status_code, expected_response",
    [
        (
            {},
            http.HTTPStatus.UNAUTHORIZED,
            {"detail": "Not authenticated. Invalid API key"},
        ),
        (
            {"x-api-key": "wrong-api-key"},
            http.HTTPStatus.UNAUTHORIZED,
            {"detail": "Not authenticated. Invalid API key"},
        ),
        (
            {"x-api-key": "api-key"},
            http.HTTPStatus.OK,
            {"message": "Authenticated"},
        ),
    ],
    ids=(
        "헤더를 전달하지 않은 경우",
        "올바르지 않은 API Key",
        "올바른 API Key",
    ),
)
def test_auth(
    headers: dict[str, str], expected_status_code: int, expected_response: dict[str, Any]
):
    response = client.get("/auth", headers=headers)

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
