import http
from typing import Annotated, Any

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


class ListItemsWithJsonList(compose.query.Query):
    filters: Json[list[dict[str, Any]]] = "[]"
    enabled_only: bool = True


@app.get("/items")
def get(q: Annotated[ListItems, compose.fastapi.as_query(ListItems)]):
    return q.model_dump()


@app.get("/items-with-json-list")
def get_with_json_list(
    q: Annotated[ListItemsWithJsonList, compose.fastapi.as_query(ListItemsWithJsonList)],
):
    return q.model_dump()


client = TestClient(app)


@pytest.mark.parametrize(
    "params, expected_response",
    [
        pytest.param(
            {
                "type": ["foo", "bar"],
                "page": 1,
                "per_page": 10,
            },
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
    expected_response: dict[str, Any],
):
    response = client.get(
        url="/items",
        params=params,
    )

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "params, expected_response",
    [
        pytest.param(
            {},
            {
                "filters": [],
                "enabled_only": True,
            },
        ),
        pytest.param(
            {
                "filters": '[{"status": "active"}]',
                "enabled_only": False,
            },
            {
                "filters": [{"status": "active"}],
                "enabled_only": False,
            },
        ),
    ],
)
def test_as_query_with_json_generic(
    params: dict[str, Any],
    expected_response: dict[str, Any],
):
    response = client.get(
        url="/items-with-json-list",
        params=params,
    )

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == expected_response
