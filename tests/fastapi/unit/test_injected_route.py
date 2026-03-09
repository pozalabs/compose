import http
import inspect
from typing import Annotated, get_origin
from unittest.mock import sentinel

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
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


@pytest.fixture
def register(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router = app.router.__class__(route_class=route_class)

    def _register(path, endpoint):
        router.add_api_route(path, endpoint, methods=["GET"])
        app.include_router(router)
        return app.routes[-1]

    return _register


def test_convert_resolvable_type(register):
    def endpoint(greeter: Greeter) -> str:
        return greeter.greet("world")

    route = register("/test", endpoint)

    annotation = route.endpoint.__annotations__["greeter"]

    assert get_origin(annotation) is Annotated


def test_preserve_non_resolvable_type(register):
    def endpoint(name: str, greeter: Greeter) -> str:
        return greeter.greet(name)

    route = register("/test/{name}", endpoint)

    assert route.endpoint.__annotations__["name"] is str


def test_skip_unannotated_parameter(register):
    def endpoint(value=42) -> str:
        return str(value)

    route = register("/test", endpoint)
    sig = inspect.signature(route.endpoint)

    assert sig.parameters["value"].default == 42


def test_skip_annotated_type(register):
    def endpoint(value: Annotated[str, "metadata"]) -> str:
        return value

    route = register("/test", endpoint)

    assert route.endpoint.__annotations__["value"] == Annotated[str, "metadata"]


def test_skip_optional_type(register):
    def endpoint(value: str | None = None) -> str:
        return value or "default"

    route = register("/test", endpoint)

    assert route.endpoint.__annotations__["value"] == str | None


def test_strip_default_from_resolvable_parameter(register):
    def endpoint(greeter: Greeter = sentinel.default) -> str:
        return greeter.greet("world")

    route = register("/test", endpoint)
    sig = inspect.signature(route.endpoint)

    assert sig.parameters["greeter"].default is inspect.Parameter.empty


def test_http_round_trip(container):
    route_class = compose.fastapi.injected_route(container)
    app = FastAPI()
    router = app.router.__class__(route_class=route_class)

    @router.get("/greet/{name}")
    def greet(name: str, greeter: Greeter) -> dict[str, str]:
        return {"message": greeter.greet(name)}

    app.include_router(router)
    setup_dishka(container, app)

    client = TestClient(app)
    response = client.get("/greet/world")

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"message": "Hello, world!"}
