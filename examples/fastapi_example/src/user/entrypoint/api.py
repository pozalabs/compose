from dependency_injector.wiring import inject
from fastapi import Depends

import compose
from src import constants
from src.dependency import provide
from src.user import schema, service
from src.user.adapter.repository import UserRepository
from src.user.domain import command

from .router import router


@router.get(
    "/v1/users/{name}",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 조회",
)
@inject
def retrieve_user(
    name: str,
    user_repository: UserRepository = Depends(provide(UserRepository)),
):
    if (user := user_repository.find_by_name(name)) is None:
        raise compose.exceptions.DoesNotExistError()

    return schema.User.model_validate(user.encode())


@router.post(
    "/v1/users",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 추가",
)
@inject
def add_user(
    cmd: command.AddUser,
    handler: service.AddUserHandler = Depends(provide(service.AddUserHandler)),
):
    return handler.handle(cmd)
