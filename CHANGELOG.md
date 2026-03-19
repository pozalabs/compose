# CHANGELOG

## v2.3.0 (2026-03-19)

### New Features

- `compose.dag` 모듈 추가: 의존성 그래프 기반 실행기(`DAGJob`, `DAGExecutor`) 제공
  - 기존 `compose.concurrent`의 `DependencyJob`/`DependencyExecutor`를 이름 변경 후 독립 모듈로 분리

### Improvements

- `auto_wired` 데코레이터가 더 다양한 callable 타입과 호환

## v2.2.0 (2026-03-10)

### Breaking Changes

**auth**

- `AuthorizationServer` 생성자 시그니처 변경
  ```python
  # before
  AuthorizationServer(base_url="https://example.com", auth_client_factory=factory)

  # after
  AuthorizationServer(auth_client_factory=factory, access_token_url="https://example.com/token")
  ```
- `JWTDecoder.decode()` 반환 타입이 authlib `JWTClaims`에서 `TokenClaims`로 변경
- `AuthorizationServer.create_authorization_url()`, `revoke_token()` 제거

**field**

- `IdField`가 `PyObjectIdField`로 이름 변경
  ```python
  id: PyObjectId = PyObjectIdField()
  ```

**asyncio / concurrent**

- `AsyncTaskExecutor.execute()`, `ThreadPoolExecutor.execute()`의 `Result` 래핑 및 `group` 파라미터 제거
  ```python
  # before
  results = await executor.execute(jobs, group=True)
  value = results[key].value

  # after
  results = await executor.execute(jobs)  # dict[K, T]
  value = results[key]
  ```

**sql**

- `SQLEntity.id` 타입이 `int | None`에서 `uuid.UUID`로 변경 (생성 시 자동 할당)
- `SQLRepository.find_by_id()`, `delete()` 파라미터 타입이 `int`에서 `uuid.UUID`로 변경

**model**

- `compose.container` 모듈이 `compose.model`로 이름 변경
  ```python
  from compose.model import BaseModel, TimeStampedModel
  ```

**event**

- `EventBus` 의존성 해결 방식이 문자열 기반에서 타입 기반으로 변경, `with_container()` 제거
  ```python
  # before
  bus = EventBus.with_container("path.to.container")

  # after
  resolver = create_event_handler_resolver(container)
  bus = EventBus(dependency_resolver=resolver)
  ```

**query**

- `Operator.then()`이 `Operator.pipe()`로 이름 변경
- `Evaluable` 제거, `deep_evaluate()` 함수로 대체
- `MongoKeyword` 제거

### Added

- `TokenClaims`: JWT 토큰 클레임 값 객체 (`sub`, `iss`, `jti`, `iat`, `exp`, `extra`)
- `AuthorizationServer.default()`, `JWTDecoder.default()`: 팩토리 메서드
- `S3ObjectStore`: S3 객체 CRUD 래퍼 (`upload`, `download`, `delete`, `copy`, `exists`)
- `compose.fastapi.injected_route()`: dishka 기반 FastAPI 라우트 자동 의존성 주입
- `compose.di`: 프레임워크 중립적 DI 패키지
- `create_event_handler_resolver()`: EventBus용 DI resolver (`compose.di.dishka`, `compose.di.dependency_injector.wiring`)
- `deep_evaluate()`: dict/list 내부 Operator의 재귀적 평가 함수
- `MongoLock.acquirer()`에 `clock` 파라미터 추가 (테스트 시 시간 주입 가능)
- `uuid7()`이 `uuid.UUID` 객체 반환 (문자열이 필요하면 `uuid7_str()` 사용)

### Fixed

- `MongoLock` TTL 인덱스가 잘못된 필드에 생성되던 버그 수정
- `MongoLock.acquire()`에서 락 획득 성공 후 불필요하게 재시도하던 버그 수정

## v2.1.0 (2026-02-27)

### Breaking Changes

**gunicorn**

- `GunicornSettings.threads` 필드 제거
- `GunicornSettings.worker_class` 기본값이 `uvicorn_worker.UvicornWorker`로 변경

**otel**

- `compose.opentelemetry` 모듈이 `compose.otel`로 이름 변경
  ```python
  from compose.otel import LoguruInstrumentor, get_default_tracer_provider
  ```

## v2.0.0 (2026-02-27)

### Breaking Changes

**BaseModel**

- Pydantic v1 호환 메서드 제거
  - `model.json()` → `model.model_dump_json()`
  - `model.dict()` → `model.model_dump()`
  - `model.copy()` → `model.model_copy()`
  - `model.encode()` → `model.model_dump(mode="json")`
- 검증이 필요한 복사는 `validated_copy()` 사용
  ```python
  updated = entity.validated_copy(update={"name": "new"})
  ```

**deprecated alias 제거**

- `EmptyOnNull` → `SkipNull`
- `MatchLookup` → `EqualityLookup`
- `Pagination` → `OffsetPagination`
- `get_default_logger()` → `create_logger()`
- `compose.deprecation` 모듈 제거

**repository**

- `MongoRepository.execute_raw()` 제거
- `MongoRepository.filter()` → `MongoRepository.paginate()`
  ```python
  result = await repo.paginate(query)  # OffsetPaginationResult 또는 CursorPaginationResult
  ```

**pagination**

- `Pagination` → `OffsetPaginationResult`로 이름 변경
- `OffsetPaginationResult.page`, `per_page` 필수화
- `CursorPaginationResult.has_next` 제거 (`next_cursor is not None`으로 판단)
- `ListSchema.from_pagination()` → `ListSchema.from_result()`
- `MongoFilterQuery` → `MongoOffsetPaginationQuery`

**query**

- 연산자 팩토리 메서드 이름 변경
  - `Group.by_null()` → `Group.without_key()`
  - `Spec.ref()` → `Spec.alias()`
  - `Project.from_attrs()` → `Project.of()`
  - `Reduce.list()` → `Reduce.into_list()`
  - `Reduce.int()` → `Reduce.into_int()`
  - `SortBy.from_()` → `SortBy.parse()`
- `Project.from_()`, `ComparisonOperator.from_()` 제거
- `Skip`, `Limit`, `Sample` 등 숫자 파라미터에 값 검증 추가 (음수/0 전달 시 `ValueError`)

**event**

- `MessageBus` → `EventBus`로 이름 변경
- `MessageConsumer(messagebus=)` → `MessageConsumer(event_bus=)`
- `MessageConsumerASGIMiddleware(messagebus=)` → `MessageConsumerASGIMiddleware(event_bus=)`
- `EventHandler.handle()`이 `async def`로 변경

**auth**

- `authlib`가 선택적 의존성으로 전환 (`compose[auth]` extra 필요)

**fastapi**

- `AutoWired` 클래스 제거, `auto_wired()` 함수 사용
- `auto_wired()`의 `with_injection` 파라미터 제거 (항상 자동 적용)
- `WithPath` → `FromPath`로 이름 변경
- `UserInjector`, `CommandUpdater`, `create_with_user()` 제거, `FromAuth`로 대체
  ```python
  auth = FromAuth(lambda: User(id="user_1"))
  cmd: Annotated[CreateItem, with_fields(CreateItem, user_id=auth.field("id", str))]
  ```
- `to_query()` 제거, `as_query()` 사용

**logging**

- `intercept()` → `route_to_loguru()`로 이름 변경

### Added

- `BaseModel.validated_copy()`: 검증을 포함한 모델 복사 메서드
- `CursorPaginationResult`, `CursorListSchema`: 커서 기반 페이지네이션
- `MongoCursorPaginationQuery`: MongoDB 커서 페이지네이션 쿼리
- `FromAuth`: 인증 정보 기반 필드 주입
- `MessageConsumer`에 `max_receive_backoff` 파라미터 추가 (peek 실패 시 지수 backoff)

### Fixed

- 다중 조회 결과 없을 때 예외 대신 빈 결과 반환으로 통일
- `MongoDbContainer` replica set의 Mac 호환성 문제 수정
