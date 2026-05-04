from typing import Self

import pytest
from pydantic import TypeAdapter, ValidationError

from compose.types import Float, Int, Str, validator


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


class PositiveInt(Int):
    @classmethod
    @validator
    def check_positive(cls, v: int) -> Self:
        if v <= 0:
            raise ValueError("must be positive")
        return cls(v)


class NonNegativeFloat(Float):
    @classmethod
    @validator
    def check_non_negative(cls, v: float) -> Self:
        if v < 0:
            raise ValueError("must be non-negative")
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


def test_base_class_validated_without_validators():
    assert Str.validated("hello") == Str("hello")
    assert Int.validated(42) == Int(42)
    assert Float.validated(3.14) == Float(3.14)


def test_pydantic_run_validator_on_deserialization():
    ta = TypeAdapter(Trimmed)

    assert ta.validate_python("  hello  ") == Trimmed("hello")


def test_pydantic_raise_validation_error_on_validator_failure():
    ta = TypeAdapter(NonBlank)

    with pytest.raises(ValidationError):
        ta.validate_python("   ")


def test_validated_apply_validator_for_int():
    assert PositiveInt.validated(5) == PositiveInt(5)

    with pytest.raises(ValueError, match="must be positive"):
        PositiveInt.validated(-1)


def test_validated_apply_validator_for_float():
    assert NonNegativeFloat.validated(1.5) == NonNegativeFloat(1.5)

    with pytest.raises(ValueError, match="must be non-negative"):
        NonNegativeFloat.validated(-0.1)
