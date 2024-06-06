import http
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import Field, Json

import compose
from compose import compat
from compose.framework.fastapi import to_query

app = FastAPI()


class ListItems(compose.query.Query):
    types: list[str] | None = Field(None, alias="type")
    filter: Json | None = None
    page: int = 1
    per_page: int = 10


@app.get("/items")
def get(q: Annotated[ListItems, Depends(to_query(ListItems))]):
    return compat.model_dump(q)


client = TestClient(app)


def test_to_query():
    response = client.get(
        url="/items",
        params={
            "type": ["foo", "bar"],
            "filter": '{"foo": "bar"}',
            "page": 2,
            "per_page": 20,
        },
    )

    expected_response = {
        "types": ["foo", "bar"],
        "filter": {"foo": "bar"},
        "page": 2,
        "per_page": 20,
    }

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == expected_response
