from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import mypy_boto3_lambda


@dataclass(frozen=True)
class Success[T]:
    payload: T


@dataclass(frozen=True)
class Failure:
    error_type: str
    message: str
    raw: dict[str, Any]


type InvocationResult[T] = Success[T] | Failure


class LambdaClient:
    def __init__(self, lambda_client: mypy_boto3_lambda.LambdaClient) -> None:
        self._client = lambda_client

    def invoke(
        self,
        function_name: str,
        payload: dict[str, Any] | None = None,
        *,
        qualifier: str | None = None,
    ) -> InvocationResult[dict[str, Any]]:
        params: dict[str, Any] = {
            "FunctionName": function_name,
            "InvocationType": "RequestResponse",
        }
        if payload is not None:
            params["Payload"] = json.dumps(payload)
        if qualifier is not None:
            params["Qualifier"] = qualifier

        response = self._client.invoke(**params)

        response_payload = json.loads(response["Payload"].read())

        if "FunctionError" in response:
            return Failure(
                error_type=response["FunctionError"],
                message=response_payload.get("errorMessage", ""),
                raw=response_payload,
            )

        return Success(payload=response_payload)

    def invoke_async(
        self,
        function_name: str,
        payload: dict[str, Any] | None = None,
        *,
        qualifier: str | None = None,
    ) -> None:
        params: dict[str, Any] = {
            "FunctionName": function_name,
            "InvocationType": "Event",
        }
        if payload is not None:
            params["Payload"] = json.dumps(payload)
        if qualifier is not None:
            params["Qualifier"] = qualifier

        self._client.invoke(**params)
