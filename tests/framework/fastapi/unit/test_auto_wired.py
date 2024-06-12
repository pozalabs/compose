import http
from typing import Any

import pytest
from dependency_injector import providers
from dependency_injector.wiring import inject
from fastapi import APIRouter, FastAPI
from starlette.testclient import TestClient

import compose


class User(compose.BaseModel):
    name: str


class UserRepository:
    def __init__(self):
        self._items = [
            User(name="user1"),
            User(name="user2"),
        ]

    def find_by_name(self, name: str) -> User | None:
        return next((item for item in self._items if item.name == name), None)


class UserContainer(compose.dependency.DeclarativeContainer):
    user_repository = providers.Singleton(UserRepository)


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    user = providers.Container(UserContainer)


provide = compose.dependency.create_provider(ApplicationContainer)
router = APIRouter()


@router.get("/v1/users/{name}", response_model=User)
@inject
@compose.fastapi.auto_wired(provide)
def retrieve_user(
    name: str,
    user_repository: UserRepository,
):
    return user_repository.find_by_name(name)


@pytest.fixture
def container():
    wirer = compose.dependency.create_wirer(packages=[])
    container = ApplicationContainer.wired(wirer=wirer, modules=[__name__])
    yield container
    container.unwire()


@pytest.fixture
def app(container: ApplicationContainer) -> FastAPI:
    app = FastAPI()
    app.container = container
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
