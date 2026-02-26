import http
from typing import Annotated

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ConfigDict

import compose


class User(compose.BaseModel):
    id: str


class CreateItem(compose.command.Command):
    name: str
    user_id: str | None = None

    model_config = ConfigDict(json_schema_extra=compose.schema.schema_excludes("user_id"))


auth = compose.fastapi.FromAuth(lambda: User(id="user_1"))


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()

    @_app.post("/items")
    def create_item(
        cmd: Annotated[
            CreateItem,
            compose.fastapi.with_fields(
                CreateItem,
                user_id=auth.field("id", str),
            ),
        ],
    ):
        return {"item_name": cmd.name, "user_id": cmd.user_id}

    return _app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def test_with_user(app: FastAPI, client: TestClient):
    response = client.post("/items", json={"name": "item_1"})

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"item_name": "item_1", "user_id": "user_1"}
