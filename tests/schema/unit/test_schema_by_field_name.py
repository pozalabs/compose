from typing import Any

import pytest
from pydantic import Field

import compose
from compose.schema.extra import schema_by_field_name

if compose.compat.IS_PYDANTIC_V2:
    from pydantic import ConfigDict


@pytest.fixture
def model_type() -> type[compose.BaseModel]:
    class Model(compose.BaseModel):
        name: str = Field(alias="username")

        if compose.compat.IS_PYDANTIC_V2:
            model_config = ConfigDict(json_schema_extra=schema_by_field_name())
        else:

            class Config:
                json_schema_extra = schema_by_field_name()

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
    assert compose.compat.model_schema(model_type) == expected
