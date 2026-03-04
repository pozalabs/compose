from __future__ import annotations

from io import BytesIO

import boto3
import botocore.exceptions
import pytest
from moto import mock_aws

from compose.aws import S3ObjectStore

BUCKET = "test-bucket"


@pytest.fixture
def store():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield S3ObjectStore(client, BUCKET)


def test_upload_bytes(store: S3ObjectStore):
    store.upload("file.txt", b"hello")

    assert store.download("file.txt") == b"hello"


def test_upload_file_object(store: S3ObjectStore):
    store.upload("file.txt", BytesIO(b"hello"))

    assert store.download("file.txt") == b"hello"


def test_upload_with_params(store: S3ObjectStore):
    store.upload("file.txt", b"hello", ContentType="text/plain")

    assert store.download("file.txt") == b"hello"


def test_download_nonexistent_key(store: S3ObjectStore):
    with pytest.raises(botocore.exceptions.ClientError):
        store.download("nonexistent")


def test_delete(store: S3ObjectStore):
    store.upload("file.txt", b"hello")
    store.delete("file.txt")

    assert not store.exists("file.txt")


def test_delete_nonexistent_key(store: S3ObjectStore):
    store.delete("nonexistent")


def test_copy(store: S3ObjectStore):
    store.upload("src.txt", b"hello")
    store.copy("src.txt", "dst.txt")

    assert store.download("dst.txt") == b"hello"


def test_copy_nonexistent_source(store: S3ObjectStore):
    with pytest.raises(botocore.exceptions.ClientError):
        store.copy("nonexistent", "dst.txt")


def test_exists_return_true_for_existing_key(store: S3ObjectStore):
    store.upload("file.txt", b"hello")

    assert store.exists("file.txt") is True


def test_exists_return_false_for_nonexistent_key(store: S3ObjectStore):
    assert store.exists("nonexistent") is False
