import http

import compose

EXCEPTION_HANDLER_INFOS = (
    compose.fastapi.ExceptionHandlerInfo.for_exc(
        exc_cls=compose.exceptions.DoesNotExistError,
        status_code=http.HTTPStatus.NOT_FOUND,
    ),
    compose.fastapi.ExceptionHandlerInfo.for_exc(
        exc_cls=compose.exceptions.DomainValidationError,
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
    ),
    compose.fastapi.ExceptionHandlerInfo.for_exc(
        exc_cls=compose.exceptions.AuthorizationError,
        status_code=http.HTTPStatus.UNAUTHORIZED,
    ),
    compose.fastapi.ExceptionHandlerInfo.for_request_validation_error(),
    compose.fastapi.ExceptionHandlerInfo.for_pydantic_validation_error(),
    compose.fastapi.ExceptionHandlerInfo.default(),
)
