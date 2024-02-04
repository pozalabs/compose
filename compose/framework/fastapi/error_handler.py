import http
from collections.abc import Callable
from typing import Self, TypeAlias

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from compose import compat, schema
from compose.container import BaseModel

ErrorHandler: TypeAlias = Callable[[Request, Exception], Response]


class ErrorHandlerInfo(BaseModel):
    exc_class_or_status_code: int | type[Exception]
    handler: ErrorHandler

    @classmethod
    def for_status_code(cls, status_code: int, error_type: str) -> Self:
        return cls(
            exc_class_or_status_code=status_code,
            handler=create_error_handler(status_code=status_code, error_type=error_type),
        )

    @classmethod
    def from_status_code(cls, status_code: http.HTTPStatus) -> Self:
        return cls.for_status_code(status_code=status_code, error_type=status_code.name.lower())

    @classmethod
    def for_exc(
        cls,
        exc_type: type[Exception],
        status_code: int,
        error_type: str,
    ) -> Self:
        return cls(
            exc_class_or_status_code=exc_type,
            handler=create_error_handler(status_code=status_code, error_type=error_type),
        )

    @classmethod
    def for_http_exception(cls, exc: HTTPException) -> Self:
        return cls.from_status_code(http.HTTPStatus(exc.status_code))


def create_error_handler(status_code: int, error_type: str) -> ErrorHandler:
    def error_handler(request: Request, exc: Exception) -> Response:
        if isinstance(exc, HTTPException):
            return JSONResponse(
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
        return JSONResponse(content=jsonable_encoder(response), status_code=status_code)

    return error_handler


def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
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
    return JSONResponse(
        content=jsonable_encoder(response),
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
    )
