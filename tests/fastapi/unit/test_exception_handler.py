import http
from unittest import mock

from fastapi import Request
from fastapi.responses import JSONResponse

import compose


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
