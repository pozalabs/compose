from typing import Callable, Generic, TypeAlias, TypeVar, final

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class _Result(Generic[T, E]):
    def unwrap(self) -> T:
        if isinstance(self, Ok):
            return self.value

        raise ValueError("Cannot unwrap value from `Err`")

    def unwrap_err(self) -> E:
        if isinstance(self, Err):
            return self.error

        raise ValueError("Cannot unwrap error from `Ok`")

    def unwrap_or(self, default: T) -> T:
        if isinstance(self, Ok):
            return self.value

        return default


@final
class Ok(_Result[T, E]):
    __match_args__ = ("value",)

    def __init__(self, value: T):
        self.value = value


@final
class Err(_Result[T, E]):
    __match_args__ = ("error",)

    def __init__(self, error: E):
        self.error = error


Result: TypeAlias = Ok | Err


def to_result(func: Callable[..., T]) -> Result:
    try:
        return Ok(func())
    except Exception as exc:
        return Err(exc)
