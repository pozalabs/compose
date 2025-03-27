import http

from fastapi import FastAPI
from fastapi.testclient import TestClient

import compose

app = FastAPI()


@app.get("/items")
def get(pagination_params: compose.fastapi.OffsetPaginationParams.as_depends()):
    return {"page": pagination_params.page, "per_page": pagination_params.per_page}


client = TestClient(app)


def test_pagination_params_injected():
    response = client.get(url="/items")

    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"page": 1, "per_page": 10}
