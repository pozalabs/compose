# CHANGELOG

## v3.2.0 (2026-06-24)

### Features

**otel**

- OTel meter provider 설정 및 FastAPI 통합 계측 함수 추가

### Dependencies

- httpx 상한을 0.29.0으로 확장
- fastapi 상한을 0.138.0으로 확장
- gunicorn 상한을 27.0.0으로 확장
- pytest 상한을 10.0.0으로 확장

## v3.1.0 (2026-06-19)

### Breaking Changes

**query.mongo**

- `func.Q` → `func.q`, `func.Pipeline` → `func.pipeline`로 소문자 함수명 컨벤션에 맞게 변경
- `Merge.dict` 팩토리 메서드를 `Merge.into_dict`로 리네임

### Features

**otel**

- `ServiceResourceAttrs`를 `otel` 모듈에서 직접 import 가능
- opentelemetry 의존성을 `otel` extra로 제공: `pip install pozalabs-compose[otel]`

### Bug Fixes

**repository**

- `Repository` 제네릭 타입 어노테이션 오류 수정

## v3.0.0 (2026-05-06)

### Breaking Changes

**types**

- Pydantic v1 bridge 레이어 제거, Pydantic v2 네이티브 설계로 전환
  - `CoreSchemaGettable`, `SupportsGetValidators`, `chain()`, `Validator`, `ValidatorGenerator` 등 호환 유틸리티 삭제
  - `ValidatablePrimitive`, `TypedList`, `StrList`, `IntList` 등 레거시 타입 삭제
  - `ListMeta` metaclass 기반 동적 타입 생성을 표준 제네릭 클래스(`List[T](list[T])`)로 대체
- 검증 내부 구조 변경: `validated()` classmethod로 명시적 검증 경로 제공
  - `__init_subclass__`로 MRO 순서대로 `@validator` 자동 수집
  - `@validator` 데코레이터 인터페이스는 기존과 동일

## v2.7.0 (2026-05-04)

### Features

**mongodb**

- `MongoRepository`의 ID 타입을 제네릭으로 확장
  - `MongoRepository[T, ID]` 형태로 두 번째 타입 파라미터 추가
  - 기본값이 `PyObjectId`이므로 기존 코드 변경 불필요
  - `str`, `int` 등 다양한 ID 타입 사용 가능

**messaging**

- `MessageQueue` 제네릭 타입 파라미터 도입
  - `push`는 `EventMessage`를 받고, `peek`/`delete`는 타입 파라미터 `M`으로 특화
  - `MessagePushable` Protocol 도입으로 발행 전용 인터페이스 분리

### Bug Fixes

**s3**

- presigned URL 생성 시 `ExpiresIn` 값을 `int`로 변환하여 시그니처 오류 방지

### Internal

- 사용처 없는 `LocalMessageQueue`, `MessageConsumerASGIMiddleware` 삭제
- 본체 코드 타입 에러 수정

## v2.6.1 (2026-04-21)

### Breaking Changes

**di**

- `dependency-injector`가 선택 의존성으로 전환
  - 사용하는 경우 `pip install pozalabs-compose[di]`로 설치
- DI 모듈의 re-export 제거

### Features

**mongodb**

- Repository 인덱스 동기화 시 Database 네임스페이스 구분 지원

**logging**

- 경과 시간 로깅 유틸리티를 `logging` 모듈로 통합

**event**

- `EventMessage`의 다형적 직렬화를 `model_config` 기반으로 전환

### Bug Fixes

**querying**

- `as_query`에서 non-dataclass metadata 포함 시 `asdict` 크래시 수정

**gunicorn**

- `export_settings` 함수 re-export 누락 수정

## v2.6.0 (2026-04-08)

### Breaking Changes

**dag**

- `DAGJob`의 func 시그니처가 `Callable[P, T]`에서 `Callable[[dict[K, T]], T]`로 변경
  - func는 의존성 결과 딕셔너리(`results`)를 받아 실행 결과를 반환
  - `results`에는 해당 job의 `dependencies`에 선언한 키의 결과만 포함
  - 고정 인자를 사용하는 경우 `DAGJob.bound()` 팩토리 메서드 사용
  - `DAGJob.bound()`의 `key`와 `func`는 positional-only

  ```python
  # Before
  DAGJob(key="a", dependencies=set(), func=add, a=1, b=2)
  DAGJob.no_dependencies(key="a", func=add, a=1, b=2)

  # After (결과 주입)
  DAGJob(key="sum", dependencies={"a", "b"}, func=lambda results: results["a"] + results["b"])

  # After (고정 인자)
  DAGJob.bound("a", add, a=1, b=2)

  # After (순서 의존 + 결과 무시)
  DAGJob(key="a", dependencies={"upstream"}, func=lambda _: add(a=1, b=2))
  ```

### Features

**logging**

- `create_logger`에 `serialize` 파라미터 추가
  - `serialize=True`로 JSON 직렬화 출력 활성화
  - 기본값 `False` (기존 동작 유지)

## v2.5.0 (2026-04-08)

### Breaking Changes

**concurrent**

- 병렬 실행기(`AsyncTaskExecutor`, `ThreadPoolExecutor`, `execute_in_pool`)의 반환 타입이 `dict[K, T]`에서 `dict[K, T | Exception]`으로 변경
  - 개별 job 실패 시 전체 실패 대신 해당 job의 결과에 `Exception` 객체 반환
  - 실행 결과는 `match/case`로 성공/실패 판별: `case Exception()` → 실패, `case T()` → 성공

## v2.4.0 (2026-04-06)

### Breaking Changes

**auth**

- `HeaderAuth` 초기화 및 팩토리 메서드 이름 변경
  - `HeaderAuth(secrets=...)` → `HeaderAuth(headers=...)`
  - `HeaderAuth.single(key=...)` → `HeaderAuth.from_api_key(api_key=...)`

**event**

- `Event` 클래스에서 제네릭 타입 파라미터 제거, id 타입을 `str`로 고정
  - `Event[PyObjectId]` → `Event` (id는 `str(uuid4())`로 자동 생성)

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
