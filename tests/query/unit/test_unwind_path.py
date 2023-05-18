import pytest

from compose.query.mongo.op import UnwindPath


def test_cannot_initiate_not_prefixed_with_dollar_sign():
    with pytest.raises(ValueError):
        UnwindPath("field")
