import http
from unittest import mock

from fastapi import Request
from fastapi.responses import JSONResponse

import compose.exceptions
from compose.framework.fastapi.error_handler import ErrorHandlerInfo


def test_error_handler_info_for_status_code():
    error_handler = ErrorHandlerInfo.for_status_code(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        error_type=http.HTTPStatus.INTERNAL_SERVER_ERROR.name.lower(),
    )
    response = error_handler.handler(mock.Mock(spec=Request), ValueError())

    content = dict(
        title="Internal Server Error",
        type="internal_server_error",
        detail=None,
        invalid_params=None,
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)

    assert isinstance(response, JSONResponse)
    assert response.render(content) == expected.render(content)
    assert response.status_code == expected.status_code


def test_error_handler_info_for_exc():
    class AuthorizationError(compose.exceptions.BaseError):
        pass

    error_handler = ErrorHandlerInfo.for_exc(
        exc_type=AuthorizationError,
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_type=AuthorizationError.__name__.lower(),
    )
    response = error_handler.handler(
        mock.Mock(spec=Request),
        AuthorizationError(message="Unauthorized", detail="Wrong password"),
    )

    content = dict(
        title="Unauthorized",
        type="authorization_error",
        detail="Wrong password",
        invalid_params=None,
    )
    expected = JSONResponse(content=content, status_code=http.HTTPStatus.UNAUTHORIZED)

    assert isinstance(response, JSONResponse)
    assert response.render(content) == expected.render(content)
    assert response.status_code == expected.status_code
