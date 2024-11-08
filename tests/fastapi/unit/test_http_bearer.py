import http
from collections.abc import Callable

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

import compose

app = FastAPI()


def http_bearer() -> compose.fastapi.HTTPBearer:
    return compose.fastapi.HTTPBearer(
        error_handlers={
            "on_credentials_missing": lambda: HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
            )
        },
    )


@app.get("/auth", dependencies=[Depends(http_bearer())])
def authed():
    return {"message": "Authenticated"}


client = TestClient(app)


@pytest.mark.parametrize(
    "get_headers, expected_status_code",
    [
        (
            lambda: {},
            http.HTTPStatus.UNAUTHORIZED,
        ),
        (
            lambda: {"Authorization": "Bearer token"},
            http.HTTPStatus.OK,
        ),
    ],
    ids=(
        "인증 헤더 누락",
        "인증 헤더 전달",
    ),
)
def test_auth(get_headers: Callable[[], dict[str, str]], expected_status_code: int):
    response = client.get("/auth", headers=get_headers())

    assert response.status_code == expected_status_code
