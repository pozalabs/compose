from __future__ import annotations

import json
from typing import TYPE_CHECKING

from compose import utils

from .. import model
from .base import MessageQueue

if TYPE_CHECKING:
    import mypy_boto3_sqs

try:
    import boto3  # noqa: F401
except ImportError:
    raise ImportError(
        "The aws extra must be installed to use the `SqsMessageQueue`. "
        "Install with package with `aws` extra (`compose[aws]`)"
    )


class SqsMessageQueue(MessageQueue):
    def __init__(
        self,
        sqs_client: mypy_boto3_sqs.SQSClient,
        queue_name: str,
        wait_time_seconds: int,
    ):
        self.client = sqs_client
        self.wait_time_seconds = wait_time_seconds

        self._queue_url = self.client.get_queue_url(QueueName=queue_name)["QueueUrl"]
        self._event_cls_map = {cls.__name__: cls for cls in utils.descendants_of(MessageQueue)}

    def push(self, message: model.SqsEventMessage) -> None:
        self.client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(message.encode(by_alias=True)),
            MessageGroupId=str(message.body.id),
            MessageDeduplicationId=str(message.body.id),
            MessageAttributes=dict(
                event_name=dict(
                    DataType="String",
                    StringValue=message.body.__class__.__name__,
                )
            ),
        )

    def peek(self) -> model.SqsEventMessage | None:
        response = self.client.receive_message(
            QueueUrl=self._queue_url,
            AttributeNames=["All"],
            MessageAttributeNames=["All"],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=self.wait_time_seconds,
        )

        messages = response.get("Messages", [])
        if not messages:
            return None

        message = next(iter(messages))
        event_name = message["MessageAttributes"]["event_name"]["StringValue"]
        event_cls = self._event_cls_map[event_name]
        event_body = json.loads(message["Body"])

        return model.SqsEventMessage(
            body=event_cls(**event_body),
            receipt_handle=message["ReceiptHandle"],
        )

    def delete(self, message: model.SqsEventMessage) -> None:
        self.client.delete_message(QueueUrl=self._queue_url, ReceiptHandle=message.receipt_handle)
