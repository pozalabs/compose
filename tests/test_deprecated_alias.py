import warnings
from typing import Self

import pytest

from compose.deprecation import ComposeDeprecationWarning, deprecated_alias


class Base:
    def __init__(self, value: int):
        self.value = value

    @classmethod
    def create(cls, value: int) -> Self:
        return cls(value=value)


Alias = deprecated_alias("Alias", Base)


def test_emit_warning():
    with pytest.warns(ComposeDeprecationWarning, match=r"`Alias`.+`Base`"):
        Alias(value=1)


def test_isinstance_compatible():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ComposeDeprecationWarning)
        instance = Alias(value=1)

    assert isinstance(instance, Base)


def test_inherit_classmethod():
    with pytest.warns(ComposeDeprecationWarning):
        instance = Alias.create(value=1)

    assert instance.value == 1
