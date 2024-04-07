import functools
import http
from collections.abc import Awaitable, Callable
from typing import ClassVar, Self, TypeAlias

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from compose import compat, schema

ExceptionHandler: TypeAlias = Callable[[Request, Exception], Response | Awaitable[Response]]


class ExceptionHandlerInfo:
    default_response_cls: ClassVar[type[Response]] = JSONResponse

    def __init__(
        self, exc_class_or_status_code: int | type[Exception], handler: ExceptionHandler
    ) -> None:
        self.exc_class_or_status_code = exc_class_or_status_code
        self.handler = handler

    @classmethod
    def for_status_code(
        cls,
        status_code: http.HTTPStatus,
        error_type: str | None = None,
        response_cls: type[Response] | None = None,
    ) -> Self:
        return cls(
            exc_class_or_status_code=status_code,
            handler=create_exception_handler(
                status_code=status_code,
                error_type=error_type or status_code.name.lower(),
                response_cls=response_cls or cls.default_response_cls,
            ),
        )

    @classmethod
    def for_exc(
        cls,
        exc_cls: type[Exception],
        status_code: int,
        error_type: str | None = None,
        response_cls: type[Response] | None = None,
    ) -> Self:
        return cls(
            exc_class_or_status_code=exc_cls,
            handler=create_exception_handler(
                status_code=status_code,
                error_type=error_type or http.HTTPStatus(status_code).name.lower(),
                response_cls=response_cls or cls.default_response_cls,
            ),
        )

    @classmethod
    def default(cls) -> Self:
        return cls(
            exc_class_or_status_code=Exception,
            handler=create_exception_handler(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                error_type=http.HTTPStatus.INTERNAL_SERVER_ERROR.name.lower(),
                response_cls=cls.default_response_cls,
            ),
        )

    @classmethod
    def for_http_exception(cls, response_cls: type[Response] | None = None) -> Self:
        return cls(
            exc_class_or_status_code=HTTPException,
            handler=create_http_exception_handler(response_cls or cls.default_response_cls),
        )

    @classmethod
    def for_request_validation_error(cls, response_cls: type[Response] | None = None) -> Self:
        return cls(
            exc_class_or_status_code=RequestValidationError,
            handler=create_validation_error_handler(response_cls or cls.default_response_cls),
        )

    @classmethod
    def for_pydantic_validation_error(cls, response_cls: type[Response] | None = None) -> Self:
        return cls(
            exc_class_or_status_code=ValidationError,
            handler=create_validation_error_handler(response_cls or cls.default_response_cls),
        )


def create_exception_handler(
    status_code: int,
    error_type: str,
    response_cls: type[Response],
) -> ExceptionHandler:
    def exception_handler(request: Request, exc: Exception) -> Response:
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

    return exception_handler


def create_http_exception_handler(response_cls: type[Response]) -> ExceptionHandler:
    def http_exception_handler(request: Request, exc: HTTPException) -> Response:
        status_code = http.HTTPStatus(exc.status_code)
        return response_cls(
            content=jsonable_encoder(
                schema.Error(
                    title=exc.detail,
                    type=status_code.name.lower(),
                )
            ),
            status_code=status_code,
            headers=exc.headers,
        )

    return http_exception_handler


def validation_error_handler(
    request: Request,
    exc: RequestValidationError | ValidationError,
    response_cls: type[Response],
) -> Response:
    response = schema.Error(
        title="Validation failed",
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


def create_validation_error_handler(response_cls: type[Response]) -> ExceptionHandler:
    return functools.partial(validation_error_handler, response_cls=response_cls)
