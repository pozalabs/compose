import uuid

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
@compose.fastapi.auto_wired(provide)
def retrieve_user(
    user_id: uuid.UUID,
    user_repository: UserRepository,
    session_factory: sessionmaker,
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
@compose.fastapi.auto_wired(provide)
def list_users(
    user_repository: UserRepository,
    session_factory: sessionmaker,
    name: str | None = None,
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
@compose.fastapi.auto_wired(provide)
def add_user(
    cmd: service.command.AddUser,
    handler: service.AddUserHandler,
):
    return handler.handle(cmd)
