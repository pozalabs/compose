from collections.abc import Callable
from typing import Any

from fastapi import Depends

from compose.container import BaseModel


class CommandUpdater:
    def __init__(self, from_field: str, to_field: str):
        self.from_field = from_field
        self.to_field = to_field

    def __call__[T: BaseModel](self, cmd: T, user: Any) -> T:
        return cmd.model_copy(update={self.to_field: getattr(user, self.from_field)}, deep=True)


def create_with_user[U](
    user_getter: Callable[[], U],
    command_updater: Callable[..., Any],
) -> Callable[..., Any]:
    def with_user[T: BaseModel](cmd_type: type[T]) -> Any:
        def inject(cmd, user: U = Depends(user_getter)) -> T:
            return command_updater(cmd, user)

        inject.__annotations__["cmd"] = cmd_type
        return Depends(inject)

    return with_user
