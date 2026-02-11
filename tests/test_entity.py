from typing import ClassVar

import pytest

import compose


def test_cannot_declare_entity_mismatched_updatable_fields():
    with pytest.raises(ValueError):

        class TestEntity(compose.entity.MongoEntity):
            field_a: str
            field_b: str

            updatable_fields: ClassVar[set[str]] = {"field_a", "field_b", "field_c"}
