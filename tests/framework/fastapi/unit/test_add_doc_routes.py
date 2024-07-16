import http

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

import compose


@pytest.fixture
def app() -> FastAPI:
    return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "docs, cond, expected_status_codes",
    [
        (
            [compose.fastapi.SwaggerUIHTML()],
            False,
            [http.HTTPStatus.NOT_FOUND],
        ),
        (
            [
                compose.fastapi.SwaggerUIHTML(),
                compose.fastapi.RedocHTML(),
                compose.fastapi.OpenAPIJson(),
            ],
            True,
            [http.HTTPStatus.OK, http.HTTPStatus.OK, http.HTTPStatus.OK],
        ),
    ],
)
def test_docs_routes_exposer(
    docs: list[compose.fastapi.OpenAPIDoc],
    cond: bool,
    expected_status_codes: list[http.HTTPStatus],
    app: FastAPI,
    client: TestClient,
):
    compose.fastapi.add_doc_routes(app=app, docs=docs, cond=cond)

    for doc, expected_status_code in zip(docs, expected_status_codes):
        response = client.get(doc.path)
        assert response.status_code == expected_status_code


def test_not_exposed_docs_not_added(app: FastAPI, client: TestClient):
    compose.fastapi.add_doc_routes(app=app, docs=[compose.fastapi.SwaggerUIHTML()], cond=True)

    assert client.get("/redoc").status_code == http.HTTPStatus.NOT_FOUND
    assert client.get("/openapi.json").status_code == http.HTTPStatus.NOT_FOUND
