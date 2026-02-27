# compose v2 마이그레이션 가이드

compose v1에서 v2로 업그레이드하기 위한 가이드

## 1. 이름 변경

검색/치환으로 해결 가능한 변경 사항

### deprecated alias

| v1 | v2 |
|---|---|
| `EmptyOnNull` | `SkipNull` |
| `MatchLookup` | `EqualityLookup` |
| `Pagination` (query stage) | `OffsetPagination` |
| `get_default_logger()` | `create_logger()` |

### 쿼리 연산자

| v1 | v2 |
|---|---|
| `Spec.ref(field, spec)` | `Spec.alias(field, spec)` |
| `Project.from_attrs(**attrs)` | `Project.of(**attrs)` |
| `Group.by_null(*ops)` | `Group.without_key(*ops)` |
| `Reduce.list(input_, in_)` | `Reduce.into_list(input_, in_)` |
| `Reduce.int(input_, in_)` | `Reduce.into_int(input_, in_)` |
| `SortBy.from_(key)` | `SortBy.parse(key)` |

### FastAPI

| v1 | v2 |
|---|---|
| `WithPath` | `FromPath` |

### 메시징

| v1 | v2 |
|---|---|
| `MessageBus` | `EventBus` |
| `MessageConsumer(messagebus=...)` | `MessageConsumer(event_bus=...)` |

### 페이지네이션 결과

| v1 | v2 |
|---|---|
| `Pagination` (결과 클래스) | `OffsetPaginationResult` |

### 스키마

| v1 | v2 |
|---|---|
| `ListSchema.from_pagination(result)` | `ListSchema.from_result(result)` |

### 로깅

| v1 | v2 |
|---|---|
| `intercept()` | `route_to_loguru()` |

## 2. 제거된 API

대체 코드가 필요한 변경 사항

### BaseModel 레거시 메서드 제거

Pydantic v1 호환을 위해 제공하던 래핑 메서드가 제거됨. Pydantic v2 네이티브 메서드를 직접 사용

```python
# v1
obj.json()
obj.dict()
obj.copy(update={"name": "new"})
obj.encode()

# v2
obj.model_dump_json()
obj.model_dump()
obj.model_copy(update={"name": "new"})
json.loads(obj.model_dump_json())
```

### BaseModel.validated_copy()

`model_copy()`에 검증을 추가한 메서드. 기존에 `model_copy(validate=True)`로 사용하던 패턴을 대체

```python
# v1
obj.model_copy(update={"name": "new"}, validate=True)

# v2
obj.validated_copy(update={"name": "new"})
```

`validated_copy()`는 복사 후 `model_validate()`를 수행하여 `validate_assignment`와 동일한 수준의 검증을 보장

### FastAPI: CommandUpdater/UserInjector/create_with_user 제거

`FromAuth` + `with_fields` 조합으로 대체

```python
# v1
from compose.fastapi import CommandUpdater, UserInjector

@router.post("/items")
def create_item(cmd: Annotated[CreateItemCommand, CommandUpdater(user_injector)]):
    ...

# v2
from compose.fastapi import FromAuth, with_fields

auth = FromAuth(get_current_user)

@router.post("/items")
def create_item(cmd: Annotated[CreateItemCommand, with_fields(
    CreateItemCommand,
    user_id=(ObjectId, Depends(auth.field("id", ObjectId))),
)]):
    ...
```

### FastAPI: AutoWired 클래스 제거

`auto_wired` 데코레이터로 대체

```python
# v1
from compose.fastapi import AutoWired

class ItemEndpoint(AutoWired):
    def __init__(self, service: ItemService):
        self.service = service

# v2
from compose.fastapi import auto_wired

@auto_wired(provider)
def create_item(service: ItemService):
    ...
```

### FastAPI: to_query() 제거

`as_query()`로 대체

```python
# v1
from compose.fastapi import to_query

SearchParams = Annotated[SearchQuery, to_query(SearchQuery)]

# v2
from compose.fastapi import as_query

SearchParams = Annotated[SearchQuery, as_query(SearchQuery)]
```

### Repository: execute_raw() 제거

타입 안전하지 않은 프록시 방식 대신, 서브클래스에서 타입이 명확한 메서드를 직접 정의

```python
# v1
repo.execute_raw("aggregate", pipeline)

# v2
class ItemRepository(MongoRepository[Item]):
    def aggregate_stats(self, pipeline: list[dict]) -> list[dict]:
        return list(self.collection.aggregate(pipeline))
```

### Repository: filter() 제거

`paginate()`로 대체. `MongoPaginationQuery`를 인자로 받아 타입이 명확한 결과를 반환

```python
# v1
result = repo.filter(qry)  # MongoFilterQuery -> Pagination (items: list[Any])

# v2
result = repo.paginate(qry)  # MongoPaginationQuery[R] -> R
```

### Query 클래스 통합

기존 `OffsetPaginationQuery`, `MongoFilterQuery`, `MongoOffsetFilterQuery`가 제거되고 두 가지 쿼리 클래스로 통합

```python
# v1
from compose.query.mongo import MongoFilterQuery, MongoOffsetFilterQuery

class ItemListQuery(MongoOffsetFilterQuery):
    ...

# v2
from compose.query.mongo import MongoOffsetPaginationQuery, MongoCursorPaginationQuery

class ItemListQuery(MongoOffsetPaginationQuery):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1)

    def to_query(self) -> list[dict]:
        return [
            Match(...).expression(),
            OffsetPagination(self.page, self.per_page).expression(),
        ]
```

### Project.from_() 제거

`Project.of()` 또는 개별 `Spec` 조합으로 대체

```python
# v1
Project.from_(field1="$source1", field2=1)

# v2 - Project.of()
Project.of(field1="$source1", field2=1)

# v2 - Spec 조합
Project(Spec.alias("field1", "$source1"), Spec.include("field2"))
```

### 로깅: get_default_logging_config(), intercept_logging() 제거

`create_logger()`가 설정, 인터셉트, 핸들러 등록을 통합 처리

```python
# v1
from compose.logging import get_default_logging_config, intercept_logging

config = get_default_logging_config(level=logging.INFO)
intercept_logging()

# v2
from compose.logging import create_logger

logger = create_logger(level=logging.INFO)
```

## 3. 동작 변경

코드 수정이 필요한 변경 사항

### EventHandler.handle()이 async로 변경

기존 동기 핸들러를 `async def handle()`로 전환해야 함

```python
# v1
class OrderCreatedHandler:
    def handle(self, evt: Event) -> None:
        self.service.process(evt)

# v2
class OrderCreatedHandler:
    async def handle(self, evt: Event) -> None:
        self.service.process(evt)
```

`EventHandler` 프로토콜이 `async def handle(self, evt: Event) -> None`을 요구하므로, 모든 핸들러가 async 메서드를 구현해야 함

### OffsetPagination/OffsetPaginationResult의 page, per_page 필수화

`page`와 `per_page`가 필수 인자로 변경됨. 전체 조회(`page=None`)는 별도 쿼리로 분리 필요

```python
# v1 - 전체 조회
result = OffsetPaginationResult(total=100, items=items)  # page=None 허용

# v2 - 페이지네이션은 page, per_page 필수
result = OffsetPaginationResult(total=100, items=items, page=1, per_page=10)

# v2 - 전체 조회는 list_by() 등 별도 쿼리 사용
items = repo.list_by(filter_)
```

`OffsetPagination` stage도 동일하게 `page`와 `per_page`가 양의 정수 필수

### Skip/Limit 값 검증 추가

`Skip`은 0 이상, `Limit`은 1 이상의 정수만 허용. 잘못된 값 전달 시 `ValueError` 발생

```python
Skip(0)   # OK
Skip(-1)  # ValueError: Expected non-negative integer, got -1

Limit(1)  # OK
Limit(0)  # ValueError: Expected positive integer, got 0
```

### create_logger()에서 level 파라미터 변경

별도의 `level` 파라미터 대신 `**config` kwargs로 전달

```python
# v1
create_logger(level=logging.DEBUG)

# v2
create_logger(level=logging.DEBUG)  # 동일하게 kwargs로 전달
```

`create_logger()`는 `**config: Unpack[BasicHandlerConfig]`를 받으므로 `level` 외에 `format`, `filter`, `colorize` 등 loguru 핸들러 설정을 직접 전달 가능

### authlib가 선택적 의존성으로 변경

`AuthorizationServer`, `JWTDecoder`, `JWTIssuer` 사용 시 authlib 설치 필요

```bash
uv add authlib
```

미설치 상태에서 import하면 `ImportError` 발생

## 4. 새로 추가된 기능

### 커서 페이지네이션

오프셋 기반 외에 커서 기반 페이지네이션 지원

쿼리 정의:

```python
from compose.query.mongo import MongoCursorPaginationQuery

class ItemCursorQuery(MongoCursorPaginationQuery):
    cursor: str | None = None
    per_page: int = 10

    def to_query(self) -> list[dict]:
        pipeline = [Match(...).expression()]
        if self.cursor:
            pipeline.append(Match(Gt("_id", ObjectId(self.cursor))).expression())
        pipeline.append(Limit(self.per_page + 1).expression())
        return pipeline

    def derive_cursor(self, last_item: dict) -> str:
        return str(last_item["_id"])
```

결과 사용:

```python
result: CursorPaginationResult = repo.paginate(query)
# result.items: list[Any]
# result.next_cursor: str | None
```

스키마 변환:

```python
from compose.schema import CursorListSchema

class ItemCursorListSchema(CursorListSchema[ItemSchema]):
    pass

schema = ItemCursorListSchema.from_result(result)
```

### FromAuth

인증 사용자 정보를 엔드포인트 파라미터로 주입

```python
from compose.fastapi import FromAuth, with_fields

auth = FromAuth(get_current_user)

@router.post("/items")
def create_item(
    cmd: Annotated[CreateItemCommand, with_fields(
        CreateItemCommand,
        user_id=auth.field("id", ObjectId),
    )],
):
    ...
```

`FromAuth(user_getter)`는 사용자 조회 함수를 받아, `field(attr, type)` 메서드로 사용자 속성을 FastAPI 의존성으로 변환

### 빈 결과 생성

페이지네이션 결과의 빈 인스턴스를 간편하게 생성

```python
# 오프셋 페이지네이션
empty = OffsetPaginationResult.empty(page=1, per_page=10)
# OffsetPaginationResult(total=0, items=[], page=1, per_page=10)

# 커서 페이지네이션
empty = CursorPaginationResult.empty()
# CursorPaginationResult(items=[], next_cursor=None)
```

### validated_copy()

`model_copy()` 후 검증까지 수행하는 메서드

```python
item = Item(name="original", quantity=5)
updated = item.validated_copy(update={"quantity": -1})
# quantity에 ge=0 제약이 있으면 ValidationError 발생
```

Pydantic의 `model_copy()`는 검증을 수행하지 않으므로, 필드 제약 조건을 보장하려면 `validated_copy()` 사용

### MessageConsumer backoff

메시지 수신 실패 시 지수 백오프의 최대 대기 시간을 설정

```python
consumer = MessageConsumer(
    event_bus=event_bus,
    message_queue=queue,
    max_receive_backoff=60,  # 최대 60초 (기본값)
)
```

연속 실패 시 `2^n`초씩 증가하되, `max_receive_backoff`를 초과하지 않음
