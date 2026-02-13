import http
from collections.abc import Callable

import pytest
from dependency_injector import providers
from fastapi import APIRouter, FastAPI
from pydantic import Field
from starlette.testclient import TestClient

import compose


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


class UserContainer(compose.dependency.DeclarativeContainer):
    user_repository = providers.Singleton(UserRepository)


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    user = providers.Container(UserContainer)


provide = compose.dependency.create_provider(ApplicationContainer)
router = APIRouter()


@compose.fastapi.auto_wired(provide, with_injection=True)
def current_user(user_repository: UserRepository):
    return user_repository.find_by_name("user1")


auto_wired = compose.fastapi.AutoWired(provider=provide, injectors={"user": current_user})


@router.get("/v1/user", response_model=User)
@auto_wired()
def retrieve_current_user(user: User):
    return user


@pytest.fixture
def container():
    container = ApplicationContainer.wired(modules=[__name__])
    yield container
    container.unwire()


# NOTE: 라우터를 사용지 않고 `app.get`으로 엔드포인트를 바로 등록하면 의존성이 주입되지 않음
@pytest.fixture
def app(container: ApplicationContainer) -> FastAPI:
    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_auto_wired(client: TestClient):
    response = client.get("/v1/user")

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"name": "user1"}
