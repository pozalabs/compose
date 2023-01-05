from typing import Any, Optional, Type

import pytest

from compose.container import BaseModel
from compose.schema.extra import schema_excludes


@pytest.fixture
def model_type() -> Type[BaseModel]:
    class Model(BaseModel):
        name: str
        age: Optional[int] = None

        class Config:
            schema_extra = schema_excludes("age")

    return Model


@pytest.fixture
def expected() -> dict[str, Any]:
    return {
        "properties": {"name": {"title": "Name", "type": "string"}},
        "required": ["name"],
        "title": "Model",
        "type": "object",
    }


def test_schema_by_field_name(model_type: Type[BaseModel], expected: dict[str, Any]):
    assert model_type.schema() == expected
