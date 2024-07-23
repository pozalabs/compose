import http

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


user_injector = compose.fastapi.UserInjector(
    user_getter=lambda: User(id="user_1"),
    command_updater=compose.fastapi.CommandUpdater(from_field="id", to_field="user_id"),
).injector()
with_user = compose.fastapi.create_with_user(user_injector)


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()

    @_app.post("/items")
    def create_item(cmd: with_user(CreateItem)):
        return {"item_name": cmd.name, "user_id": cmd.user_id}

    return _app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def test_with_user(app: FastAPI, client: TestClient):
    response = client.post("/items", json={"name": "item_1"})

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"item_name": "item_1", "user_id": "user_1"}
