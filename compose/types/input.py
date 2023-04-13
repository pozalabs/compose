from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Expressionable(Protocol):
    def expression(self) -> Any:
        ...


class Input:
    def __init__(self, value: Any):
        self.value = value

    def unwrap(self) -> Any:
        return self.value.expression() if isinstance(self.value, Expressionable) else self.value
