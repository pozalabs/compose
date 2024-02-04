from collections.abc import Sequence
from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel, Field, create_model

from compose import compat

if compat.IS_PYDANTIC_V2:
    from pydantic._internal._utils import lenient_issubclass
else:
    from pydantic.utils import lenient_issubclass

Q = TypeVar("Q", bound=BaseModel)
SequenceTypes = (list, set, tuple, frozenset, Sequence)


def to_query(q: type[Q], /) -> type[Q]:
    field_args = (
        "title",
        "alias",
        "default",
        "default_factory",
        "description",
    )

    if compat.IS_PYDANTIC_V2:
        field_definitions = {
            field_name: (
                field_info.annotation,
                (
                    Query(**{arg: getattr(field_info, arg, None) for arg in field_args})
                    if lenient_issubclass(field_info.annotation, SequenceTypes)
                    else field_info
                ),
            )
            for field_name, field_info in q.model_fields.items()
        }
    else:
        field_definitions = {
            field_name: (
                Field(Query(**{arg: getattr(field, arg, None) for arg in field_args}))
                if lenient_issubclass(field.outer_type_, SequenceTypes)
                else field
            )
            for field_name, field in q.__fields__.items()
        }

    return create_model(f"{q.__name__}Query", **field_definitions)
