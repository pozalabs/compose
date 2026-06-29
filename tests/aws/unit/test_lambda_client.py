from __future__ import annotations

import io
import json
from unittest import mock

import pytest
from pydantic import BaseModel

import compose


def _make_response(
    payload: dict, *, function_error: str | None = None, status_code: int = 200
) -> dict:
    response: dict = {
        "StatusCode": status_code,
        "Payload": io.BytesIO(json.dumps(payload).encode()),
    }
    if function_error is not None:
        response["FunctionError"] = function_error
    return response


@pytest.fixture
def boto_client():
    return mock.Mock()


def test_invoke_return_parsed_payload(boto_client: mock.Mock):
    response_payload = {"result": "ok"}
    boto_client.invoke.return_value = _make_response(response_payload)
    client = compose.aws.LambdaClient(boto_client)

    result = client.invoke("my-fn", payload={"key": "value"})

    assert result == response_payload


def test_invoke_without_payload(boto_client: mock.Mock):
    boto_client.invoke.return_value = _make_response({"result": "ok"})
    client = compose.aws.LambdaClient(boto_client)

    client.invoke("my-fn")

    call_kwargs = boto_client.invoke.call_args[1]
    assert "Payload" not in call_kwargs


def test_invoke_with_qualifier(boto_client: mock.Mock):
    boto_client.invoke.return_value = _make_response({"result": "ok"})
    client = compose.aws.LambdaClient(boto_client)

    client.invoke("my-fn", qualifier="v1")

    call_kwargs = boto_client.invoke.call_args[1]
    assert call_kwargs["Qualifier"] == "v1"


def test_invoke_raise_on_function_error(boto_client: mock.Mock):
    error_payload = {"errorMessage": "something went wrong", "errorType": "RuntimeError"}
    boto_client.invoke.return_value = _make_response(error_payload, function_error="Unhandled")
    client = compose.aws.LambdaClient(boto_client)

    with pytest.raises(compose.aws.LambdaInvocationError, match="something went wrong") as exc_info:
        client.invoke("my-fn")

    assert exc_info.value.error_type == "Unhandled"
    assert exc_info.value.raw == error_payload


def test_invoke_raise_with_empty_error_message(boto_client: mock.Mock):
    error_payload = {"errorType": "RuntimeError"}
    boto_client.invoke.return_value = _make_response(error_payload, function_error="Handled")
    client = compose.aws.LambdaClient(boto_client)

    with pytest.raises(compose.aws.LambdaInvocationError) as exc_info:
        client.invoke("my-fn")

    assert exc_info.value.error_type == "Handled"
    assert str(exc_info.value) == ""


def test_invoke_async_call_with_event_type(boto_client: mock.Mock):
    boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(boto_client)

    client.invoke_async("my-fn", payload={"key": "value"})

    call_kwargs = boto_client.invoke.call_args[1]
    assert call_kwargs["InvocationType"] == "Event"


def test_invoke_async_without_payload(boto_client: mock.Mock):
    boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(boto_client)

    client.invoke_async("my-fn")

    call_kwargs = boto_client.invoke.call_args[1]
    assert "Payload" not in call_kwargs


def test_invoke_async_with_qualifier(boto_client: mock.Mock):
    boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(boto_client)

    client.invoke_async("my-fn", qualifier="v2")

    call_kwargs = boto_client.invoke.call_args[1]
    assert call_kwargs["Qualifier"] == "v2"


class Request(BaseModel):
    user_id: int
    name: str


def test_invoke_with_pydantic_model_payload(boto_client: mock.Mock):
    boto_client.invoke.return_value = _make_response({"result": "ok"})
    client = compose.aws.LambdaClient(boto_client)

    client.invoke("my-fn", payload=Request(user_id=1, name="alice"))

    call_kwargs = boto_client.invoke.call_args[1]
    assert json.loads(call_kwargs["Payload"]) == {"user_id": 1, "name": "alice"}


def test_invoke_async_with_pydantic_model_payload(boto_client: mock.Mock):
    boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(boto_client)

    client.invoke_async("my-fn", payload=Request(user_id=1, name="alice"))

    call_kwargs = boto_client.invoke.call_args[1]
    assert json.loads(call_kwargs["Payload"]) == {"user_id": 1, "name": "alice"}
