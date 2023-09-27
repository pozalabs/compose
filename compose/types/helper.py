from collections.abc import Callable
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class Validatable:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        get_validators = getattr(cls, "__get_validators__", lambda: [])
        return core_schema.no_info_after_validator_function(
            create_chain(*get_validators()),
            handler(cls.__mro__[-2]),
        )


def create_chain(*_validators: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def chain(_v: Any) -> Any:
        _result = _v
        for _validator in _validators:
            _result = _validator(_result)
        return _result

    return chain
