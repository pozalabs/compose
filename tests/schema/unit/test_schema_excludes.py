from typing import Any, Optional, Type

import pytest
from pydantic import ConfigDict

import compose
from compose.container import BaseModel
from compose.schema.extra import schema_excludes


@pytest.fixture
def model_type() -> Type[BaseModel]:
    class Model(BaseModel):
        id: compose.types.PyObjectId
        name: str
        age: Optional[int] = None

        model_config = ConfigDict(json_schema_extra=schema_excludes("age"))

    return Model


@pytest.fixture
def expected() -> dict[str, Any]:
    return {
        "additionalProperties": False,
        "properties": {"name": {"title": "Name", "type": "string"}},
        "required": ["name"],
        "title": "Model",
        "type": "object",
    }


def test_schema_by_field_name(model_type: Type[BaseModel], expected: dict[str, Any]):
    assert model_type.model_json_schema() == expected
