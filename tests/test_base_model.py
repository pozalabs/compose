import pytest
from pydantic import ValidationError

import compose


class Model(compose.BaseModel):
    name: str


class SchemaModel(compose.schema.Schema):
    name: str


def test_model_validate():
    model = Model(name="test")
    assert SchemaModel.model_validate(model.dict()) == SchemaModel(name="test")


def test_validate_on_copy():
    model = Model(name="test")

    with pytest.raises(ValidationError):
        model.copy(
            update={"name": [1, 2, 3]},
            validate=True,
        )
