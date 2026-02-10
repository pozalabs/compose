import http
from unittest import mock

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

import compose
from compose import schema


def test_error_handler_info_for_status_code():
    error_handler = compose.fastapi.ExceptionHandlerInfo.for_status_code(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        error_type=http.HTTPStatus.INTERNAL_SERVER_ERROR.name.lower(),
    )
    response = error_handler.handler(mock.Mock(spec=Request), ValueError("Invalid value"))

    content = dict(
        title="Invalid value",
        type="internal_server_error",
        detail=None,
        invalid_params=None,
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)

    assert isinstance(response, JSONResponse)
    assert response.body == expected.body
    assert response.status_code == expected.status_code


def test_error_handler_info_for_exc():
    class AuthorizationError(compose.exceptions.BaseError):
        pass

    error_handler = compose.fastapi.ExceptionHandlerInfo.for_exc(
        exc_cls=AuthorizationError,
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_type=http.HTTPStatus.UNAUTHORIZED.name.lower(),
    )
    response = error_handler.handler(
        mock.Mock(spec=Request),
        AuthorizationError(message="Unauthorized", detail="Wrong password"),
    )

    content = dict(
        title="Unauthorized",
        type="unauthorized",
        detail="Wrong password",
        invalid_params=None,
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.UNAUTHORIZED)

    assert isinstance(response, JSONResponse)
    assert response.body == expected.body
    assert response.status_code == expected.status_code


def test_error_handler_info_for_exc_with_custom_error_schema():
    class CustomError(schema.Error):
        code: str = "custom_code"

    class AuthorizationError(compose.exceptions.BaseError):
        pass

    error_handler = compose.fastapi.ExceptionHandlerInfo.for_exc(
        exc_cls=AuthorizationError,
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_type=http.HTTPStatus.UNAUTHORIZED.name.lower(),
        error_schema_cls=CustomError,
    )
    response = error_handler.handler(
        mock.Mock(spec=Request),
        AuthorizationError(message="Unauthorized", detail="Wrong password"),
    )

    content = dict(
        title="Unauthorized",
        type="unauthorized",
        detail="Wrong password",
        invalid_params=None,
        code="custom_code",
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.UNAUTHORIZED)

    assert isinstance(response, JSONResponse)
    assert response.body == expected.body
    assert response.status_code == expected.status_code


def test_exception_handler_info_subclass_with_default_error_schema():
    class CustomError(schema.Error):
        code: str = "subclass_code"

    class CustomExceptionHandlerInfo(compose.fastapi.ExceptionHandlerInfo):
        default_error_schema_cls = CustomError

    error_handler = CustomExceptionHandlerInfo.for_status_code(
        status_code=http.HTTPStatus.BAD_REQUEST,
    )
    response = error_handler.handler(mock.Mock(spec=Request), ValueError("Bad request"))

    content = dict(
        title="Bad request",
        type="bad_request",
        detail=None,
        invalid_params=None,
        code="subclass_code",
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.BAD_REQUEST)

    assert isinstance(response, JSONResponse)
    assert response.body == expected.body
    assert response.status_code == expected.status_code


def test_default_exception_handlers_return_default_set():
    handlers = compose.fastapi.default_exception_handlers()

    exc_classes = [h.exc_class_or_status_code for h in handlers]
    assert exc_classes == [
        compose.exceptions.DoesNotExistError,
        compose.exceptions.NotAllowedError,
        compose.exceptions.DomainValidationError,
        compose.exceptions.AuthorizationError,
        RequestValidationError,
        ValidationError,
        Exception,
    ]


def test_default_exception_handlers_include_extras():
    custom = compose.fastapi.ExceptionHandlerInfo.for_exc(
        ValueError,
        http.HTTPStatus.BAD_REQUEST,
    )

    handlers = compose.fastapi.default_exception_handlers(custom)

    exc_classes = [h.exc_class_or_status_code for h in handlers]
    assert exc_classes == [
        compose.exceptions.DoesNotExistError,
        compose.exceptions.NotAllowedError,
        compose.exceptions.DomainValidationError,
        compose.exceptions.AuthorizationError,
        ValueError,
        RequestValidationError,
        ValidationError,
        Exception,
    ]


def test_default_exception_handlers_use_subclass():
    class CustomExceptionHandlerInfo(compose.fastapi.ExceptionHandlerInfo):
        pass

    handlers = compose.fastapi.default_exception_handlers(
        handler_info_cls=CustomExceptionHandlerInfo,
    )

    assert all(isinstance(h, CustomExceptionHandlerInfo) for h in handlers)
