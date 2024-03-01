import functools
import http
from collections.abc import Callable
from typing import Self, TypeAlias

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError

from compose import compat, schema
from compose.container import BaseModel

ErrorHandler: TypeAlias = Callable[[Request, Exception], Response]


class ErrorHandlerInfo(BaseModel):
    exc_class_or_status_code: int | type[Exception]
    handler: ErrorHandler

    @classmethod
    def for_status_code(
        cls, status_code: int, error_type: str, response_cls: type[Response]
    ) -> Self:
        return cls(
            exc_class_or_status_code=status_code,
            handler=create_error_handler(
                status_code=status_code,
                error_type=error_type,
                response_cls=response_cls,
            ),
        )

    @classmethod
    def from_status_code(cls, status_code: http.HTTPStatus, response_cls: type[Response]) -> Self:
        return cls.for_status_code(
            status_code=status_code,
            error_type=status_code.name.lower(),
            response_cls=response_cls,
        )

    @classmethod
    def for_exc(
        cls,
        exc_type: type[Exception],
        status_code: int,
        error_type: str,
        response_cls: type[Response],
    ) -> Self:
        return cls(
            exc_class_or_status_code=exc_type,
            handler=create_error_handler(
                status_code=status_code,
                error_type=error_type,
                response_cls=response_cls,
            ),
        )

    @classmethod
    def for_http_exception(cls, exc: HTTPException, response_cls: type[Response]) -> Self:
        return cls.from_status_code(
            status_code=http.HTTPStatus(exc.status_code),
            response_cls=response_cls,
        )

    @classmethod
    def request_validation_error(cls, response_cls: type[Response]) -> Self:
        return cls(
            exc_class_or_status_code=RequestValidationError,
            handler=create_validation_error_handler(response_cls),
        )

    @classmethod
    def pydantic_validation_error(cls, response_cls: type[Response]) -> Self:
        return cls(
            exc_class_or_status_code=ValidationError,
            handler=create_validation_error_handler(response_cls),
        )


def create_error_handler(
    status_code: int,
    error_type: str,
    response_cls: type[Response],
) -> ErrorHandler:
    def error_handler(request: Request, exc: Exception) -> Response:
        if isinstance(exc, HTTPException):
            return response_cls(
                content=jsonable_encoder(getattr(exc, "detail")),
                status_code=exc.status_code,
            )

        response = schema.Error(
            title=str(exc),
            type=error_type,
            detail=getattr(exc, "detail", None),
            invalid_params=(
                (invalid_params := getattr(exc, "invalid_params", None))
                and [
                    compat.model_validate(t=schema.InvalidParam, obj=invalid_param)
                    for invalid_param in invalid_params
                ]
            ),
        )
        return response_cls(content=jsonable_encoder(response), status_code=status_code)

    return error_handler


def create_validation_error_handler(response_cls: type[Response]) -> ErrorHandler:
    return functools.partial(validation_exception_handler, response_cls=response_cls)


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError,
    response_cls: type[Response],
) -> Response:
    response = schema.Error(
        title="validation_error",
        type="validation_error",
        invalid_params=[
            schema.InvalidParam(
                loc=".".join(str(v) for v in error["loc"]),
                message=error["msg"],
                type=error["type"],
            )
            for error in exc.errors()
        ],
    )
    return response_cls(
        content=jsonable_encoder(response),
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
    )
