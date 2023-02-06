import pytest

from compose.query.mongo.op.types import MongoKeyword


@pytest.mark.parametrize(
    "py_keyword, expected",
    [
        ("from_", MongoKeyword("from")),
        ("let", MongoKeyword("let")),
        ("local_field", MongoKeyword("localField")),
    ],
    ids=(
        "Python 키워드가 포함된 문자는 접미사를 제거",
        "한 단어로 구성된 문자는 입력과 출력이 동일",
        "두 단어 이상으로 구성된 문자는 카멜 케이스로 변환",
    ),
)
def test_mongo_keyword_from_py(py_keyword: str, expected: MongoKeyword):
    assert MongoKeyword.from_py(py_keyword) == expected


@pytest.mark.parametrize("keyword", ["local_field"], ids=("MongoDB 키워드로 사용할 수 없는 문자열은 초기화 실패",))
def test_cannot_initiate_mongo_keyword(keyword: str):
    with pytest.raises(ValueError):
        MongoKeyword(keyword)
