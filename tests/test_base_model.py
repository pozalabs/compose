import pytest
from pydantic import ValidationError

import compose


class Model(compose.BaseModel):
    name: str


class SchemaModel(compose.schema.Schema):
    name: str


def test_validated_copy_raise_validation_error_for_invalid_update():
    model = Model(name="test")

    with pytest.raises(ValidationError):
        model.validated_copy(update={"name": [1, 2, 3]})


def test_from_model():
    model = Model(name="test")
    actual = SchemaModel.from_model(model)
    expected = SchemaModel(name="test")

    assert actual == expected
