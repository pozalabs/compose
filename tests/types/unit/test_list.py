from typing import Any, Self

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomStrList(compose.types.List[str]): ...


class CustomIntList(compose.types.List[int]): ...


def test_list_str_valid():
    assert TypeAdapter(CustomStrList).validate_python(["1", "2", "3"]) == CustomStrList(
        ["1", "2", "3"]
    )


def test_list_int_valid():
    assert TypeAdapter(CustomIntList).validate_python([1, 2, 3]) == CustomIntList([1, 2, 3])
    assert TypeAdapter(CustomIntList).validate_python([1.0, 2.0, 3.0]) == CustomIntList([1, 2, 3])


@pytest.mark.parametrize(
    "value",
    [[1, 2, 3], [1.1, 2.2, 3.3], "test", 123],
)
def test_list_str_invalid(value: Any):
    with pytest.raises(ValidationError):
        TypeAdapter(CustomStrList).validate_python(value)


def test_list_int_invalid():
    with pytest.raises(ValidationError):
        TypeAdapter(CustomIntList).validate_python("test")


def test_list_generic_alias_equality():
    type1 = compose.types.List[str]
    type2 = compose.types.List[str]

    assert type1 == type2


class NonBlank(compose.types.Str):
    @classmethod
    @compose.types.validator
    def check_not_blank(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("must not be blank")
        return cls(v)


class NonBlankList(compose.types.List[NonBlank]): ...


def test_list_element_validation_via_pydantic():
    ta = TypeAdapter(NonBlankList)

    assert ta.validate_python(["a", "b"]) == NonBlankList([NonBlank("a"), NonBlank("b")])


def test_list_element_validation_reject_invalid_element():
    ta = TypeAdapter(NonBlankList)

    with pytest.raises(ValidationError):
        ta.validate_python(["a", "  "])


class MaxLen2(compose.types.List[int]):
    @classmethod
    @compose.types.validator
    def check_max_length(cls, v: list[int]) -> Self:
        if len(v) > 2:
            raise ValueError("length must be <= 2")
        return cls(v)


class SortedIntList(compose.types.List[int]):
    @classmethod
    @compose.types.validator
    def sort_values(cls, v: list[int]) -> Self:
        return cls(sorted(v))


class BoundedList(compose.types.List[int]):
    @classmethod
    @compose.types.validator
    def check_max_length(cls, v: list[int]) -> Self:
        if len(v) > 3:
            raise ValueError("length must be <= 3")
        return cls(v)


class BoundedSortedList(BoundedList):
    @classmethod
    @compose.types.validator
    def sort_values(cls, v: list[int]) -> Self:
        return cls(sorted(v))


def test_validated_apply_validator():
    assert MaxLen2.validated([1, 2]) == MaxLen2([1, 2])


def test_validated_reject_invalid():
    with pytest.raises(ValueError, match="length must be <= 2"):
        MaxLen2.validated([1, 2, 3])


def test_validated_transform():
    assert SortedIntList.validated([3, 1, 2]) == SortedIntList([1, 2, 3])


def test_validated_return_type():
    result = SortedIntList.validated([3, 1, 2])

    assert type(result) is SortedIntList


def test_inherit_validators_in_base_to_derived_order():
    assert BoundedSortedList.validated([3, 1, 2]) == BoundedSortedList([1, 2, 3])


def test_derived_validator_see_result_of_base_validator():
    with pytest.raises(ValueError, match="length must be <= 3"):
        BoundedSortedList.validated([4, 3, 2, 1])


def test_pydantic_run_validator_on_deserialization():
    ta = TypeAdapter(SortedIntList)

    assert ta.validate_python([3, 1, 2]) == SortedIntList([1, 2, 3])


def test_pydantic_raise_validation_error_on_validator_failure():
    ta = TypeAdapter(MaxLen2)

    with pytest.raises(ValidationError):
        ta.validate_python([1, 2, 3])
