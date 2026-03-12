from typing import Annotated

from fastapi import Query

import compose
from compose.query.mongo import op
from src import constants
from src.user import schema, service
from src.user.adapter.repository import UserRepository
from src.user.domain import command, query

from .router import router


@router.get(
    "/v1/users/{name}",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 조회",
)
def retrieve_user(
    name: str,
    user_repository: UserRepository,
):
    if (user := user_repository.find_by_name(name)) is None:
        raise compose.exceptions.DoesNotExistError()

    return schema.User.model_validate(user.model_dump(mode="json"))


@router.get(
    "/v1/users/emails/{email}",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 조회",
)
def retrieve_user_by_email(
    email: str,
    user_repository: UserRepository,
):
    if (user := user_repository.find_by(op.func.Q(op.Eq("email", email)))) is None:
        raise compose.exceptions.DoesNotExistError()

    return schema.User.model_validate(user.model_dump(mode="json"))


@router.get(
    "/v1/users",
    response_model=compose.schema.ListSchema[schema.User],
    tags=[constants.OpenApiTag.USER],
    summary="유저 목록 조회",
)
def list_users(
    qry: Annotated[query.ListUsers, Query()],
    user_repository: UserRepository,
):
    result = user_repository.paginate(qry)
    return compose.schema.ListSchema[schema.User].from_result(result)


@router.get(
    "/v1/users/recent",
    response_model=compose.schema.CursorListSchema[schema.User],
    tags=[constants.OpenApiTag.USER],
    summary="최근 유저 목록 조회 (커서 페이지네이션)",
)
def list_recent_users(
    qry: Annotated[query.ListRecentUsers, Query()],
    user_repository: UserRepository,
):
    result = user_repository.paginate(qry)
    return compose.schema.CursorListSchema[schema.User].from_result(result)


@router.post(
    "/v1/users",
    response_model=schema.User,
    tags=[constants.OpenApiTag.USER],
    summary="유저 추가",
)
def add_user(
    cmd: command.AddUser,
    handler: service.AddUserHandler,
):
    return handler.handle(cmd)
