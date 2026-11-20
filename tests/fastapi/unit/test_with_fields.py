import http
from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import ConfigDict, Field, model_validator

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


class RenameItem(compose.command.Command):
    item_id: int
    name: str
    memo: str | None = None
    user: User


class Verification(compose.BaseModel):
    email: str


class ChangeEmail(compose.command.Command):
    email: str
    verification: Verification

    @model_validator(mode="after")
    def check_verified(self):
        if self.email != self.verification.email:
            raise ValueError("email is not verified")
        return self


class TagItem(compose.command.Command):
    item_id: int
    tag_name: str = Field(alias="tagName")

    model_config = ConfigDict(populate_by_name=False)


auth = compose.fastapi.FromAuth(lambda: User(id="user_1"))


def get_verification() -> Verification:
    return Verification(email="verified@example.com")


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

    @_app.patch("/items/{item_id}/name")
    def rename_item(
        cmd: Annotated[
            RenameItem,
            compose.fastapi.with_fields(
                RenameItem,
                item_id=compose.fastapi.FromPath.int(),
                user=(User, Depends(lambda: User(id="user_1"))),
            ),
        ],
    ):
        return cmd.model_dump()

    @_app.patch("/items/{item_id}/memo")
    def update_item_memo(
        cmd: Annotated[
            RenameItem,
            compose.fastapi.with_fields(
                RenameItem,
                item_id=compose.fastapi.FromPath.int(),
                user=(User, Depends(lambda: User(id="user_1"))),
            ),
        ],
    ):
        return cmd.model_dump(exclude_unset=True)

    @_app.patch("/email")
    def change_email(
        cmd: Annotated[
            ChangeEmail,
            compose.fastapi.with_fields(
                ChangeEmail,
                verification=(Verification, Depends(get_verification)),
            ),
        ],
    ):
        return cmd.model_dump()

    @_app.post("/items/{item_id}/tags")
    def tag_item(
        cmd: Annotated[
            TagItem,
            compose.fastapi.with_fields(TagItem, item_id=compose.fastapi.FromPath.int()),
        ],
    ):
        return {"item_id": cmd.item_id, "tag_name": cmd.tag_name}

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


def test_accept_body_without_injected_fields_declared_required(client: TestClient):
    response = client.patch("/items/1/name", json={"name": "item_name"})

    assert response.json() == {
        "item_id": 1,
        "name": "item_name",
        "memo": None,
        "user": {"id": "user_1"},
    }


def test_exclude_unsent_body_fields_from_fields_set(client: TestClient):
    response = client.patch("/items/1/memo", json={"name": "item_name"})

    assert response.json() == {"item_id": 1, "name": "item_name", "user": {"id": "user_1"}}


def test_use_injected_values_over_body_values(client: TestClient):
    response = client.patch(
        "/items/1/name",
        json={"name": "item_name", "item_id": 2, "user": {"id": "user_2"}},
    )

    assert response.json() == {
        "item_id": 1,
        "name": "item_name",
        "memo": None,
        "user": {"id": "user_1"},
    }


def test_validate_model_with_injected_value(client: TestClient):
    response = client.patch("/email", json={"email": "verified@example.com"})

    assert response.json() == {
        "email": "verified@example.com",
        "verification": {"email": "verified@example.com"},
    }


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"email": "other@example.com"}, id="without_body_value"),
        pytest.param(
            {"email": "other@example.com", "verification": {"email": "other@example.com"}},
            id="with_forged_body_value",
        ),
    ],
)
def test_cannot_pass_model_validator_without_matching_injected_value(
    payload: dict[str, Any], client: TestClient
):
    response = client.patch("/email", json=payload)

    assert (response.status_code, response.json()) == (
        http.HTTPStatus.UNPROCESSABLE_ENTITY,
        {
            "detail": [
                {
                    "type": "value_error",
                    "loc": ["body"],
                    "msg": "Value error, email is not verified",
                    "ctx": {"error": {}},
                }
            ]
        },
    )


def test_report_body_field_error_with_body_location(client: TestClient):
    response = client.patch("/items/1/name", json={"name": 1})

    assert [error["loc"] for error in response.json()["detail"]] == [["body", "name"]]


def test_validate_alias_field_of_model_disallowing_population_by_name(client: TestClient):
    response = client.post("/items/1/tags", json={"tagName": "tag"})

    assert response.json() == {"item_id": 1, "tag_name": "tag"}


def test_exclude_injected_fields_from_openapi_body_schema(client: TestClient):
    response = client.get("/openapi.json")

    assert response.json()["components"]["schemas"]["RenameItem"] == {
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "memo": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Memo"},
        },
        "required": ["name"],
        "title": "RenameItem",
        "type": "object",
    }


def test_generate_openapi_for_model_excluding_injected_fields_by_schema_excludes(
    client: TestClient,
):
    response = client.get("/openapi.json")

    assert response.json()["components"]["schemas"]["UpdateItem"] == {
        "properties": {"name": {"title": "Name", "type": "string"}},
        "required": ["name"],
        "title": "UpdateItem",
        "type": "object",
    }
