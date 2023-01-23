import enum
from typing import Any, ClassVar, Optional, Union


class BaseError(Exception):
    default_message: ClassVar[Optional[str]] = None

    def __init__(
        self,
        message: Optional[Union[str, enum.Enum]] = None,
        detail: Optional[Any] = None,
        invalid_params: Optional[list[dict[str, Any]]] = None,
    ):
        if isinstance(message, enum.Enum):
            message = message.value
        super().__init__(message)

        if message is None and self.default_message is None:
            raise ValueError("`message` or `default_message` must not be None")

        self.message = str(message) if message is not None else self.default_message
        self.detail = detail
        self.invalid_params = invalid_params

    def __str__(self):
        return self.message
