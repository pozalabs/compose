import compose


class Model(compose.BaseModel):
    id: compose.types.PyObjectId


def test_py_object_id_schema_type_is_string():
    actual = Model.model_json_schema()

    expected = {
        "properties": {"id": {"title": "Id", "type": "string"}},
        "required": ["id"],
        "title": "Model",
        "type": "object",
    }

    assert actual == expected
