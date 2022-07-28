from typing import ClassVar

import pytest

from compose.entity import Entity


def test_entity_id_field_ordered_first():
    class TestEntity(Entity):
        field_a: str
        field_b: str

    actual = list(TestEntity.__fields__.keys())
    expected = ["id", "field_a", "field_b", "created_at", "updated_at"]

    assert actual == expected


def test_cannot_declare_entity_mismatched_updatable_fields():
    with pytest.raises(ValueError):

        class TestEntity(Entity):
            field_a: str
            field_b: str

            updatable_fields: ClassVar[set[str]] = {"field_a", "field_b", "field_c"}
