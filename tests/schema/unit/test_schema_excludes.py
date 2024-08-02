from typing import Any

import pytest
from pydantic import ConfigDict

import compose


@pytest.fixture
def model_type() -> type[compose.BaseModel]:
    class Model(compose.BaseModel):
        id: compose.types.PyObjectId
        name: str
        age: int | None = None

        model_config = ConfigDict(json_schema_extra=compose.schema.schema_excludes("age"))

    return Model


@pytest.fixture
def expected() -> dict[str, Any]:
    return {
        "properties": {
            "id": {"title": "Id", "type": "string"},
            "name": {"title": "Name", "type": "string"},
        },
        "required": ["id", "name"],
        "title": "Model",
        "type": "object",
    }


def test_schema_excludes(model_type: type[compose.BaseModel], expected: dict[str, Any]):
    assert model_type.model_json_schema() == expected
