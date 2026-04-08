import http
import urllib.parse
from collections.abc import Callable
from typing import Annotated, Any

import pytest
from dependency_injector import providers
from fastapi import APIRouter, FastAPI, Query
from pydantic import Field
from starlette.testclient import TestClient

import compose
from compose.di.dependency_injector import DeclarativeContainer, create_provider


class User(compose.BaseModel):
    name: str


class ListUsers(compose.query.Query):
    names: list[str] = Field(default_factory=list, alias="name")

    def to_query(self) -> Callable[[User], bool]:
        def filter_(user: User) -> bool:
            return user.name in self.names

        return filter_


class UserRepository:
    def __init__(self):
        self._items = [
            User(name="user1"),
            User(name="user2"),
        ]

    def find_by_name(self, name: str) -> User | None:
        return next((item for item in self._items if item.name == name), None)

    def filter(self, qry: ListUsers) -> list[User]:
        filter_users = qry.to_query()
        return [item for item in self._items if filter_users(item)]


class UserContainer(DeclarativeContainer):
    user_repository = providers.Singleton(UserRepository)


class ApplicationContainer(DeclarativeContainer):
    user = providers.Container(UserContainer)


provide = create_provider(ApplicationContainer)
router = APIRouter()


@router.get("/v1/users", response_model=list[User])
@compose.fastapi.auto_wired(provide)
def list_users(
    qry: Annotated[ListUsers, Query()],
    user_repository: UserRepository,
):
    return user_repository.filter(qry)


@router.get("/v1/users/{name}", response_model=User)
@compose.fastapi.auto_wired(provide)
def retrieve_user(
    name: str,
    user_repository: UserRepository,
):
    return user_repository.find_by_name(name)


@pytest.fixture
def container():
    container = ApplicationContainer.wired(modules=[__name__])
    yield container
    container.unwire()


# NOTE: 라우터를 사용지 않고 `app.get`으로 엔드포인트를 바로 등록하면 의존성이 주입되지 않음
@pytest.fixture
def app(container: ApplicationContainer) -> FastAPI:
    app = FastAPI()
    app.container = container  # type: ignore[missing-attribute]
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "name, expected_status_code, expected_response",
    [
        ("user1", http.HTTPStatus.OK, {"name": "user1"}),
        ("user2", http.HTTPStatus.OK, {"name": "user2"}),
    ],
)
def test_auto_wired(
    client: TestClient,
    name: str,
    expected_status_code: int,
    expected_response: dict[str, Any],
):
    response = client.get(f"/v1/users/{name}")

    assert response.status_code == expected_status_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "qry, expected_status_code, expected_response",
    [
        (ListUsers(names=["user1"]), http.HTTPStatus.OK, [{"name": "user1"}]),
        (ListUsers(names=["user3"]), http.HTTPStatus.OK, []),
    ],
)
def test_with_query_model(
    client: TestClient,
    qry: ListUsers,
    expected_status_code: int,
    expected_response: list[dict[str, Any]],
):
    response = client.get(
        "/v1/users", params=urllib.parse.urlencode(qry.model_dump(by_alias=True), doseq=True)
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
