import http

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import compose

app = FastAPI()


@app.get("/items")
def get(pagination_params: compose.fastapi.OffsetPaginationParams.as_depends()):
    return {"page": pagination_params.page, "per_page": pagination_params.per_page}


client = TestClient(app)


@pytest.mark.parametrize(
    "params, expected",
    [
        (None, dict(page=1, per_page=10)),
        (dict(page=1, per_page=20), dict(page=1, per_page=20)),
        (dict(page=2, per_page=10), dict(page=2, per_page=10)),
    ],
)
def test_pagination_params_injected(params: dict[str, int] | None, expected: dict[str, int]):
    response = client.get(url="/items", params=params)

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == expected
