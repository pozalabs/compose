import http
from typing import Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient

import compose

app = FastAPI()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
api_key_auth = compose.fastapi.APIKeyAuth(
    api_key_factory=lambda: "api-key",
    header=api_key_header,
).authenticator()


@app.get("/auth/api-key", dependencies=[Depends(api_key_auth)])
def authed_by_api_key():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "api_key, expected_status_code, expected_response",
    [
        (
            "wrong-api-key",
            http.HTTPStatus.UNAUTHORIZED,
            {"detail": "Not authenticated. Invalid API key"},
        ),
        (
            "api-key",
            http.HTTPStatus.OK,
            {"message": "Authenticated"},
        ),
    ],
    ids=(
        "올바르지 않은 API Key",
        "올바른 API Key",
    ),
)
def test_auth(api_key: str, expected_status_code: int, expected_response: dict[str, Any]):
    response = client.get("/auth/api-key", headers={"X-API-Key": api_key})

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
