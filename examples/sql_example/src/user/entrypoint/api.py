from dependency_injector.wiring import inject
from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from src import constants
from src.dependency import provide
from src.user import schema, service
from src.user.adapter.repository import UserRepository

import compose

from .router import router


@router.get(
    "/v1/users/{user_id}",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 조회",
)
@inject
def retrieve_user(
    user_id: int,
    user_repository: UserRepository = Depends(provide(UserRepository)),
    session_factory: sessionmaker = Depends(provide(sessionmaker)),
):
    with session_factory() as session:
        if (user := user_repository.find_by_id(user_id, session)) is None:
            raise compose.exceptions.DoesNotExistError()

        return schema.User.model_validate(user.model_dump(mode="json"))


@router.get(
    "/v1/users",
    response_model=list[schema.User],
    tags=[constants.OpenApiTag.USER],
    summary="유저 목록 조회",
)
@inject
def list_users(
    name: str | None = None,
    user_repository: UserRepository = Depends(provide(UserRepository)),
    session_factory: sessionmaker = Depends(provide(sessionmaker)),
):
    filter_ = {}
    if name is not None:
        filter_["name"] = name

    with session_factory() as session:
        users = user_repository.list_by(filter_, session)
        return [schema.User.model_validate(u.model_dump(mode="json")) for u in users]


@router.post(
    "/v1/users",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 추가",
)
@inject
def add_user(
    cmd: service.command.AddUser,
    handler: service.AddUserHandler = Depends(provide(service.AddUserHandler)),
):
    return handler.handle(cmd)
