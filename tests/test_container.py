from compose.container import TimeStampedModel


def test_time_stamped_model_timestamp_fields_are_ordered_last():
    class Model(TimeStampedModel):
        field_a: str
        field_b: str

    actual = list(Model.__fields__.keys())
    expected = ["field_a", "field_b", "created_at", "updated_at"]

    assert actual == expected
