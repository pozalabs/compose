import http
from typing import Annotated, Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ConfigDict

import compose


class User(compose.BaseModel):
    id: str


class UpdateItem(compose.command.Command):
    item_id: int | None = None
    name: str

    model_config = ConfigDict(json_schema_extra=compose.schema.schema_excludes("item_id"))


class UpdateItemWithUser(compose.command.Command):
    item_id: int | None = None
    name: str
    user_id: str | None = None

    model_config = ConfigDict(
        json_schema_extra=compose.schema.schema_excludes("item_id", "user_id")
    )


auth = compose.fastapi.FromAuth(lambda: User(id="user_1"))


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()

    @_app.patch("/items/{item_id}")
    def update_item(
        cmd: Annotated[
            UpdateItem,
            compose.fastapi.with_fields(
                UpdateItem,
                item_id=compose.fastapi.FromPath.int(),
            ),
        ],
    ):
        return {"item_id": cmd.item_id, "item_name": cmd.name}

    @_app.patch("/user/items/{item_id}")
    def update_item_with_user(
        cmd: Annotated[
            UpdateItemWithUser,
            compose.fastapi.with_fields(
                UpdateItemWithUser,
                item_id=compose.fastapi.FromPath.int(),
                user_id=auth.field("id", str),
            ),
        ],
    ):
        return {"item_id": cmd.item_id, "item_name": cmd.name, "user_id": cmd.user_id}

    return _app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "endpoint, payload, expected",
    [
        (
            "/items/1",
            {"name": "item_name"},
            {"item_id": 1, "item_name": "item_name"},
        ),
        (
            "/user/items/1",
            {"name": "item_name"},
            {"item_id": 1, "item_name": "item_name", "user_id": "user_1"},
        ),
    ],
)
def test_with_fields(
    endpoint: str,
    payload: dict[str, Any],
    expected: dict[str, Any],
    client: TestClient,
):
    response = client.patch(endpoint, json=payload)

    assert response.json() == expected


def test_with_fields_raise_validation_error_on_invalid_depends(client: TestClient):
    response = client.patch("/items/not_integer", json={"name": "item_name"})

    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
