import mimetypes
from pathlib import Path

import pytest

import compose


@pytest.fixture()
def register_mime_types() -> None:
    compose.types.MimeType.register(
        compose.types.MimeTypeInfo(type="application/x-new-type", ext=".new_type")
    )


@pytest.fixture()
def unregister_mime_types() -> None:
    mimetypes.types_map.pop(".new_type")


@pytest.mark.usefixtures("register_mime_types")
def test_guess():
    actual = compose.types.MimeType.guess(Path("path/to/file.new_type"))
    expected = compose.types.MimeType("application/x-new-type")

    assert actual == expected


@pytest.mark.usefixtures("unregister_mime_types")
def test_guess_without_register():
    actual = compose.types.MimeType.guess(Path("path/to/file.new_type"))
    expected = compose.types.MimeType.default()

    assert actual == expected
