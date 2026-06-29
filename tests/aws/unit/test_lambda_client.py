from __future__ import annotations

import io
import json
from unittest import mock

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


@mock.patch("boto3.client")
def test_invoke_return_success(mock_boto_client: mock.Mock):
    response_payload = {"result": "ok"}
    mock_boto_client.invoke.return_value = _make_response(response_payload)
    client = compose.aws.LambdaClient(mock_boto_client)

    result = client.invoke("my-fn", payload={"key": "value"})

    assert result == compose.aws.Success(payload=response_payload)
    mock_boto_client.invoke.assert_called_once_with(
        FunctionName="my-fn",
        InvocationType="RequestResponse",
        Payload=json.dumps({"key": "value"}),
    )


@mock.patch("boto3.client")
def test_invoke_without_payload(mock_boto_client: mock.Mock):
    mock_boto_client.invoke.return_value = _make_response({"result": "ok"})
    client = compose.aws.LambdaClient(mock_boto_client)

    client.invoke("my-fn")

    call_kwargs = mock_boto_client.invoke.call_args[1]
    assert "Payload" not in call_kwargs


@mock.patch("boto3.client")
def test_invoke_with_qualifier(mock_boto_client: mock.Mock):
    mock_boto_client.invoke.return_value = _make_response({"result": "ok"})
    client = compose.aws.LambdaClient(mock_boto_client)

    client.invoke("my-fn", qualifier="v1")

    call_kwargs = mock_boto_client.invoke.call_args[1]
    assert call_kwargs["Qualifier"] == "v1"


@mock.patch("boto3.client")
def test_invoke_return_failure_on_function_error(mock_boto_client: mock.Mock):
    error_payload = {"errorMessage": "something went wrong", "errorType": "RuntimeError"}
    mock_boto_client.invoke.return_value = _make_response(error_payload, function_error="Unhandled")
    client = compose.aws.LambdaClient(mock_boto_client)

    result = client.invoke("my-fn")

    assert result == compose.aws.Failure(
        error_type="Unhandled",
        message="something went wrong",
        raw=error_payload,
    )


@mock.patch("boto3.client")
def test_invoke_return_failure_with_empty_error_message(mock_boto_client: mock.Mock):
    error_payload = {"errorType": "RuntimeError"}
    mock_boto_client.invoke.return_value = _make_response(error_payload, function_error="Handled")
    client = compose.aws.LambdaClient(mock_boto_client)

    result = client.invoke("my-fn")

    assert isinstance(result, compose.aws.Failure)
    assert result.message == ""


@mock.patch("boto3.client")
def test_invoke_async_call_with_event_type(mock_boto_client: mock.Mock):
    mock_boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(mock_boto_client)

    client.invoke_async("my-fn", payload={"key": "value"})

    mock_boto_client.invoke.assert_called_once_with(
        FunctionName="my-fn",
        InvocationType="Event",
        Payload=json.dumps({"key": "value"}),
    )


@mock.patch("boto3.client")
def test_invoke_async_without_payload(mock_boto_client: mock.Mock):
    mock_boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(mock_boto_client)

    client.invoke_async("my-fn")

    call_kwargs = mock_boto_client.invoke.call_args[1]
    assert "Payload" not in call_kwargs


@mock.patch("boto3.client")
def test_invoke_async_with_qualifier(mock_boto_client: mock.Mock):
    mock_boto_client.invoke.return_value = {"StatusCode": 202}
    client = compose.aws.LambdaClient(mock_boto_client)

    client.invoke_async("my-fn", qualifier="v2")

    call_kwargs = mock_boto_client.invoke.call_args[1]
    assert call_kwargs["Qualifier"] == "v2"
