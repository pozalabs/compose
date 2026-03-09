import http
import inspect
from typing import Annotated
from unittest.mock import sentinel

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import DishkaRoute, setup_dishka
from fastapi import FastAPI
from starlette.testclient import TestClient

import compose


class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


class AppProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def greeter(self) -> Greeter:
        return Greeter()


@pytest.fixture
def container():
    return make_async_container(AppProvider())


def test_route_class_extend_dishka_route(container):
    route_class = compose.fastapi.injected_route(container)

    assert issubclass(route_class, DishkaRoute)


def test_convert_resolvable_type(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test")
    def endpoint(greeter: Greeter) -> str:
        return greeter.greet("world")

    app.include_router(router_with_route)
    route = app.routes[-1]

    assert route.endpoint.__annotations__["greeter"] is not Greeter


def test_preserve_non_resolvable_type(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test/{name}")
    def endpoint(name: str, greeter: Greeter) -> str:
        return greeter.greet(name)

    app.include_router(router_with_route)
    route = app.routes[-1]

    assert route.endpoint.__annotations__["name"] is str


def test_skip_unannotated_parameter(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test")
    def endpoint(value=42) -> str:
        return str(value)

    app.include_router(router_with_route)
    route = app.routes[-1]
    sig = inspect.signature(route.endpoint)

    assert sig.parameters["value"].default == 42


def test_skip_annotated_type(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test")
    def endpoint(value: Annotated[str, "metadata"]) -> str:
        return value

    app.include_router(router_with_route)
    route = app.routes[-1]

    assert route.endpoint.__annotations__["value"] == Annotated[str, "metadata"]


def test_skip_optional_type(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test")
    def endpoint(value: str | None = None) -> str:
        return value or "default"

    app.include_router(router_with_route)
    route = app.routes[-1]

    assert route.endpoint.__annotations__["value"] == str | None


def test_convert_parameter_with_default(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/test")
    def endpoint(greeter: Greeter = sentinel.default) -> str:
        return greeter.greet("world")

    app.include_router(router_with_route)
    route = app.routes[-1]
    sig = inspect.signature(route.endpoint)

    assert sig.parameters["greeter"].default is inspect.Parameter.empty


def test_http_round_trip(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router_with_route = app.router.__class__(route_class=route_class)

    @router_with_route.get("/greet/{name}")
    def greet(name: str, greeter: Greeter) -> dict[str, str]:
        return {"message": greeter.greet(name)}

    app.include_router(router_with_route)
    setup_dishka(container, app)

    client = TestClient(app)
    response = client.get("/greet/world")

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"message": "Hello, world!"}
