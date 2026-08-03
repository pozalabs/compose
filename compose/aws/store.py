from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any

import botocore.exceptions

if TYPE_CHECKING:
    import mypy_boto3_s3
    from mypy_boto3_s3.type_defs import CopySourceTypeDef, PutObjectRequestTypeDef


class S3Store:
    def __init__(self, s3_client: mypy_boto3_s3.S3Client, bucket: str) -> None:
        self._client = s3_client
        self._bucket = bucket

    def upload(self, key: str, body: bytes | IO[bytes], **kwargs: Any) -> None:
        params: PutObjectRequestTypeDef = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": body,
            **kwargs,
        }
        self._client.put_object(**params)

    def download(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def copy(self, src_key: str, dst_key: str) -> None:
        copy_source: CopySourceTypeDef = {"Bucket": self._bucket, "Key": src_key}
        self._client.copy_object(
            Bucket=self._bucket,
            Key=dst_key,
            CopySource=copy_source,
        )

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as exc:
            if exc.response["Error"]["Code"] == "404":
                return False
            raise exc
