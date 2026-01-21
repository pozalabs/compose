from __future__ import annotations

import itertools
import subprocess
from typing import TYPE_CHECKING

from ..types import Byte, MimeType, Seconds

if TYPE_CHECKING:
    import mypy_boto3_s3


def overlay_streams(
    *urls: *tuple[str, ...],
    chunk_size: Byte,
    codec: str,
) -> bytes:
    cmd = [
        "ffmpeg",
        "--recv_buffer_size",
        str(chunk_size),
        *itertools.chain.from_iterable((("-i", url) for url in urls)),
        "-filter_complex",
        f"amix=inputs={len(urls)}:duration=longest:normalize=0",
        "-c:a",
        codec,
        "-f",
        "wav",
        "-loglevel",
        "error",
        "-",
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, stderr = process.communicate()

    if process.returncode != 0:
        raise ValueError(f"Failed to overlay streams: {stderr.decode()}")

    return output


class S3AudioStreamOverlayer:
    def __init__(
        self,
        s3_client: mypy_boto3_s3.S3Client,
        bucket: str,
        expires_in: Seconds = Seconds.from_minutes(10),
    ):
        self.s3_client = s3_client
        self.bucket = bucket
        self.expires_in = expires_in

    def overlay(
        self,
        *keys: *tuple[str, ...],
        chunk_size: Byte = Byte.from_mib(5),
        codec: str,
        dst: str,
    ) -> None:
        result = overlay_streams(
            *(
                self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=int(self.expires_in),
                )
                for key in keys
            ),
            chunk_size=chunk_size,
            codec=codec,
        )

        self.s3_client.put_object(
            Body=result,
            Bucket=self.bucket,
            Key=dst,
            ContentType=MimeType.guess(dst),
        )
