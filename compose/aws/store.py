from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any

import botocore.exceptions

if TYPE_CHECKING:
    import mypy_boto3_s3
    from mypy_boto3_s3.type_defs import CopySourceTypeDef, PutObjectRequestTypeDef


class S3Store:
    def __init__(self, s3_client: mypy_boto3_s3.S3Client, bucket: str) -> None:
        self.client = s3_client
        self.bucket = bucket

    def upload(self, key: str, body: bytes | IO[bytes], **kwargs: Any) -> None:
        params: PutObjectRequestTypeDef = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": body,
            **kwargs,
        }
        self.client.put_object(**params)

    def download(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def copy(self, src_key: str, dst_key: str) -> None:
        copy_source: CopySourceTypeDef = {"Bucket": self.bucket, "Key": src_key}
        self.client.copy_object(
            Bucket=self.bucket,
            Key=dst_key,
            CopySource=copy_source,
        )

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as exc:
            if exc.response["Error"]["Code"] == "404":
                return False
            raise exc
