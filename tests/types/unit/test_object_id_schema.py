import compose


class TestModel(compose.BaseModel):
    id: compose.types.PyObjectId


def test_py_object_id_schema_type_is_string():
    actual = compose.compat.model_schema(TestModel)

    expected = {
        "properties": {"id": {"title": "Id", "type": "string"}},
        "required": ["id"],
        "title": "TestModel",
        "type": "object",
    }

    assert actual == expected
