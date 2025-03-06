from collections.abc import Generator

import pytest
from testcontainers.localstack import LocalStackContainer

pytest_plugins = [
    "compose.testing.plugin.test_type_marker",
]


@pytest.fixture(scope="session", autouse=True)
def start_localstack() -> Generator[LocalStackContainer, None, None]:
    localstack = LocalStackContainer(
        "localstack/localstack:2.0.2",
        region_name="ap-northeast-2",
    ).with_services("sqs")

    localstack.start()

    yield localstack
    localstack.stop()
