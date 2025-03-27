from typing import Self

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class Name(compose.types.Str):
    @classmethod
    @compose.types.validator
    def validate_name(cls, v: str) -> Self:
        if len(v) > 10:
            raise ValueError("Name should be less than 10 characters")

        return cls(v)


ta = TypeAdapter(Name)


def test_valid():
    assert ta.validate_python("valid name") == Name("valid name")


def test_invalid():
    with pytest.raises(ValidationError):
        ta.validate_python("Too long name")


class NameWithoutValidator(compose.types.Str): ...


class Person(compose.BaseModel):
    name: NameWithoutValidator


@pytest.mark.parametrize(
    "name",
    [
        NameWithoutValidator("valid name"),
        Person(name=NameWithoutValidator("valid name")).name,
    ],
)
def test_casting(name: NameWithoutValidator | str):
    assert isinstance(name, NameWithoutValidator) is True
