from typing import Self

import pytest
from pydantic import TypeAdapter, ValidationError

from compose.types import Str, validator


class Trimmed(Str):
    @classmethod
    @validator
    def strip_whitespace(cls, v: str) -> Self:
        return cls(v.strip())


class NonBlank(Trimmed):
    @classmethod
    @validator
    def check_not_blank(cls, v: str) -> Self:
        if not v:
            raise ValueError("must not be blank")
        return cls(v)


def test_validated_apply_validator():
    assert Trimmed.validated("  hello  ") == Trimmed("hello")


def test_direct_construction_skip_validator():
    assert Trimmed("  hello  ") == Trimmed("  hello  ")


def test_inherit_validators_in_base_to_derived_order():
    assert NonBlank.validated(" x ") == NonBlank("x")


def test_derived_validator_see_result_of_base_validator():
    with pytest.raises(ValueError, match="must not be blank"):
        NonBlank.validated("   ")


def test_pydantic_run_validator_on_deserialization():
    ta = TypeAdapter(Trimmed)

    assert ta.validate_python("  hello  ") == Trimmed("hello")


def test_pydantic_raise_validation_error_on_validator_failure():
    ta = TypeAdapter(NonBlank)

    with pytest.raises(ValidationError):
        ta.validate_python("   ")
