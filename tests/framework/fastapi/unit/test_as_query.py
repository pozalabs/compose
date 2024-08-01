import http
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Field, Json

import compose

app = FastAPI()


class ListItems(compose.query.Query):
    types: list[str] | None = Field(None, alias="type")
    filter: Json | None = None
    page: int = 1
    per_page: int = 10


@app.get("/items")
def get(q: compose.fastapi.as_query(ListItems)):
    return compose.compat.model_dump(q)


client = TestClient(app)


@pytest.mark.parametrize(
    "params, expected_status_code, expected_response",
    [
        pytest.param(
            {
                "type": ["foo", "bar"],
                "page": 1,
                "per_page": 10,
            },
            http.HTTPStatus.OK,
            {
                "types": ["foo", "bar"],
                "filter": None,
                "page": 1,
                "per_page": 10,
            },
        ),
        pytest.param(
            {
                "type": ["foo", "bar"],
                "filter": '{"foo": "bar"}',
                "page": 1,
                "per_page": 10,
            },
            http.HTTPStatus.OK,
            {
                "types": ["foo", "bar"],
                "filter": {"foo": "bar"},
                "page": 1,
                "per_page": 10,
            },
        ),
    ],
)
def test_as_query(
    params: dict[str, Any],
    expected_status_code: int,
    expected_response: dict[str, Any],
):
    response = client.get(
        url="/items",
        params=params,
    )

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == expected_response
