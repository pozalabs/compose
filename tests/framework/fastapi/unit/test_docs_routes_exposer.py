import http

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

import compose

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
client = TestClient(app)


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
):
    compose.fastapi.docs_routes_exposer(docs=docs, cond=cond)(app)

    for doc, expected_status_code in zip(docs, expected_status_codes):
        response = client.get(doc.path)
        assert response.status_code == expected_status_code
