from typing import Any, Type

import pytest
from pydantic import Field

from compose.container import BaseModel
from compose.schema.extra import schema_by_field_name


@pytest.fixture
def model_type() -> Type[BaseModel]:
    class Model(BaseModel):
        name: str = Field(alias="username")

        class Config:
            schema_extra = schema_by_field_name()

    return Model


@pytest.fixture
def expected() -> dict[str, Any]:
    return {
        "properties": {"name": {"title": "Username", "type": "string"}},
        "required": ["username"],
        "title": "Model",
        "type": "object",
    }


def test_schema_by_field_name(model_type: Type[BaseModel], expected: dict[str, Any]):
    assert model_type.schema() == expected
