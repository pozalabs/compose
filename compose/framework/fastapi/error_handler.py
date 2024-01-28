import http
from collections.abc import Callable
from typing import TypeAlias

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from compose import schema
from compose.container import BaseModel

ErrorHandler: TypeAlias = Callable[[Request, Exception], Response]


class ExceptionHandlerInfo(BaseModel):
    exc_class_or_status_code: int | type[Exception]
    handler: ErrorHandler


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
