# CHANGELOG

## v2.2.0

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
