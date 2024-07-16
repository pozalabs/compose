import http

import pytest

import compose


@pytest.mark.parametrize(
    "status_codes, expected",
    [
        (
            (http.HTTPStatus.NOT_FOUND, http.HTTPStatus.UNPROCESSABLE_ENTITY),
            {404: {"model": compose.schema.Error}, 422: {"model": compose.schema.Error}},
        ),
    ],
)
def test_additional_responses_with_default_schema(
    status_codes: tuple[int],
    expected: dict[int, dict[str, dict[str, str]]],
):
    responses = compose.fastapi.additional_responses(*status_codes)
    assert responses == expected


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
def test_additional_responses_with_response_schema(
    schema_type: type[compose.BaseModel],
    status_codes: tuple[int],
    expected: dict[int, dict[str, dict[str, str]]],
):
    responses = compose.fastapi.additional_responses(*status_codes, schema_type=schema_type)
    assert responses == expected
