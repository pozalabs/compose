from typing import Any

import pytest
from pydantic import ConfigDict, Field

import compose


@pytest.fixture
def model_type() -> type[compose.BaseModel]:
    class Model(compose.BaseModel):
        name: str = Field(alias="username")

        model_config = ConfigDict(json_schema_extra=compose.schema.schema_by_field_name())

    return Model


@pytest.fixture
def expected() -> dict[str, Any]:
    return {
        "properties": {"name": {"title": "Username", "type": "string"}},
        "required": ["username"],
        "title": "Model",
        "type": "object",
    }


def test_schema_by_field_name(model_type: type[compose.BaseModel], expected: dict[str, Any]):
    assert model_type.model_json_schema() == expected
