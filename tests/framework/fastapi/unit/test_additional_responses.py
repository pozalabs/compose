import http

import pytest

import compose


@pytest.mark.parametrize(
    "schema_type, status_codes, expected",
    [
        (
            compose.schema.Error,
            (http.HTTPStatus.NOT_FOUND, http.HTTPStatus.UNPROCESSABLE_ENTITY),
            {404: {"model": compose.schema.Error}, 422: {"model": compose.schema.Error}},
        ),
        (
            compose.schema.Schema,
            (http.HTTPStatus.NOT_FOUND, http.HTTPStatus.UNPROCESSABLE_ENTITY),
            {404: {"model": compose.schema.Schema}, 422: {"model": compose.schema.Schema}},
        ),
    ],
)
def test_additional_responses(
    schema_type: type[compose.BaseModel] | None,
    status_codes: tuple[int],
    expected: dict[int, dict[str, dict[str, str]]],
):
    responses = compose.fastapi.additional_responses(schema_type, *status_codes)
    assert responses == expected
