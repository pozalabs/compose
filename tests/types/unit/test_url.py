import pytest

import compose


def test_cannot_instantiate_s3_content_url_without_base_url():
    with pytest.raises(ValueError):
        compose.types.S3ContentUrl("filename.png")


@pytest.mark.parametrize(
    "base_url, value, expected",
    [
        (
            "https://cdn.example.com",
            "path/filename.png",
            "https://cdn.example.com/path/filename.png",
        ),
        (
            "https://cdn.example.com",
            "path/filename 1.png",
            "https://cdn.example.com/path/filename%201.png",
        ),
        (
            "https://cdn.example.com",
            "path/filename%201.png",
            "https://cdn.example.com/path/filename%201.png",
        ),
        (
            "https://cdn.example.com",
            "https://cdn.example.com/path/filename 1.png",
            "https://cdn.example.com/path/filename%201.png",
        ),
    ],
    ids=(
        "입력을 quote하지 않아도 되는 경우 `base_url`에 입력을 그대로 붙인다.",
        "입력을 quote해야 하는 경우 `base_url`에 quote한 입력을 붙인다.",
        "입력이 이미 quote된 경우 quote를 수행하지 않는다.",
        "`base_url`에 이미 포함된 URL이 입력으로 주어진 경우 `base_url`을 제외하고 quote한다.",
    ),
)
def test_s3_content_url(base_url: str, value: str, expected: str):
    actual = compose.types.S3ContentUrl.with_base_url(base_url)(value)

    assert actual == expected
