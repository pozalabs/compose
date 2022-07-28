from compose.container import BaseModel
from compose.types import PyObjectId


def test_pyobject_id_schema_type_is_string():
    class TestModel(BaseModel):
        id: PyObjectId

    actual = TestModel.schema()
    expected = {
        "properties": {"id": {"title": "Id", "type": "string"}},
        "required": ["id"],
        "title": "TestModel",
        "type": "object",
    }

    assert actual == expected
