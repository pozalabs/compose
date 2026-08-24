# compose 모듈 인덱스

심볼의 존재와 위치를 안내하는 발견용 인덱스. 시그니처와 동작은 소스와 LSP가 정본이므로 여기서 기술하지 않음. 조합 방식과 구조는 compose-ddd 스킬 참조

## 모듈 지도

### 도메인 모델링

- Pydantic 기반 모델 정의: `compose.BaseModel` / `TimeStampedModel`
- 도메인 엔티티 정의: `compose.entity` 모듈
- 도메인 명령 정의: `compose.command.Command` / `UserCommand`
- 도메인 이벤트 정의: `compose.event.Event`
- 검증된 원시 타입 정의: `compose.types.Str` / `Int` / `Float` / `List` / `Byte`
- 날짜/시간 타입: `compose.types.DateTime` / `DateRange` / `Seconds` / `MilliSeconds`
- 콘텐츠 타입 정보: `compose.types.MimeType` / `MimeTypeInfo` / `ContentDisposition`
- S3 오브젝트 URL 생성: `compose.types.create_s3_object_url`
- MongoDB ObjectId 타입: `compose.types.PyObjectId` (mongo)
- 커스텀 타입 검증 정의: `compose.types.validator`
- 에러 계층 구조: `compose.exceptions` 모듈
- 모델 필드 유틸리티: `compose.field` 모듈
- 환경 구분, enum 유틸리티: `compose.enums` 모듈

### 영속성

- 추상 저장소 인터페이스: `compose.repository.BaseRepository`
- MongoDB 저장소: `compose.repository.MongoRepository` / `MongoDocument` (mongo)
- MongoDB 인덱스 설정: `compose.repository.setup_indexes` (mongo)
- 선언적 필드 일치 조회 정의: `compose.repository.finder` / `lister` (mongo)
- SQL 저장소: `compose.repository.SQLRepository` (sql)
- 추상 쿼리 인터페이스: `compose.query.Query`
- MongoDB 쿼리: `compose.query.MongoQuery` (mongo)
- MongoDB 페이지네이션 쿼리: `compose.query.MongoPaginationQuery` / `MongoOffsetPaginationQuery` / `MongoCursorPaginationQuery` (mongo)
- MongoDB 쿼리 연산자 조합: `compose.query.mongo.op` 모듈 (mongo)
- MongoDB 트랜잭션 관리: `compose.uow.MongoUnitOfWork` / `mongo_transactional` (mongo)
- SQL 트랜잭션 관리: `compose.uow.SQLUnitOfWork` / `sql_transactional` (sql)
- 페이지네이션 결과 모델: `compose.pagination` 모듈
- API 응답 스키마: `compose.schema.Schema` / `TimeStampedSchema`
- 목록 응답 스키마: `compose.schema.ListSchema` / `CursorListSchema`
- 에러/ID 응답 모델: `compose.schema.Error` / `InvalidParam` / `Id`
- 스키마 필드 유틸리티: `compose.schema.schema_by_field_name` / `schema_excludes`

### 메시징

- 이벤트 버스: `compose.messaging.EventBus`
- 이벤트 발행: `compose.messaging.EventPublisher` / `MessagePushable`
- 이벤트 메시지 모델: `compose.messaging.EventMessage` / `SqsEventMessage`
- 메시지 소비: `compose.messaging.MessageConsumer`
- 컨슈머 실행: `compose.messaging.FastAPIMessageConsumerRunner` / `ThreadMessageConsumerRunner`
- 메시지 큐 인터페이스: `compose.messaging.MessageQueue`
- SQS 메시지 큐: `compose.messaging.SqsMessageQueue` (aws)
- 시그널 핸들링: `compose.messaging.SignalHandler` / `DefaultSignalHandler` / `ThreadSignalHandler`

### 인프라

- 의존성 주입 컨테이너: `compose.di` 모듈 (dependency-injector 또는 dishka)
- 리소스 서버 인증: `compose.auth.ResourceServer`
- 인증 값 객체: `compose.auth.AuthorizationGrant` / `TokenClaims` / `UserResource`
- JWT 발급/검증: `compose.auth.JWTDecoder` / `JWTIssuer` (jwt)
- OAuth 인가 서버: `compose.auth.AuthorizationServer` (oauth)
- AWS Parameter Store 기반 설정 관리: `compose.settings` 모듈
- 분산 락 실패 예외: `compose.lock.LockAcquisitionFailedError`
- MongoDB 분산 락: `compose.lock.MongoLock` / `MongoLockAcquirer` (mongo)
- 구조화 로깅: `compose.logging` 모듈 (loguru)
- HTTP 헤더 인증: `compose.httpx.HeaderAuth` (httpx)

### 프레임워크 통합

- API 라우터: `compose.fastapi.APIRouter` (fastapi)
- 헬스체크 엔드포인트: `compose.fastapi.add_health_check_endpoint` / `health_check` / `SpecialEndpoint` (fastapi)
- 예외 핸들러: `compose.fastapi.ExceptionHandler` / `ExceptionHandlerInfo` / `create_exception_handler` / `default_exception_handlers` (fastapi)
- OpenAPI 문서화: `compose.fastapi.add_doc_routes` / `OpenAPIDoc` / `OpenAPISchema` / `RedocHTML` / `SwaggerUIHTML` / `additional_responses` / `openapi_tags` (fastapi)
- OTel 비계측 URL 설정: `compose.fastapi.NonInstrumentedUrls` (fastapi)
- 요청 파라미터 추출: `compose.fastapi.FromAuth` / `FromPath` / `OffsetPaginationParams` / `as_query` / `with_fields` (fastapi)
- HTTP 응답: `compose.fastapi.NoContentResponse` / `ZipStreamingResponse` (fastapi)
- 인증 스킴: `compose.fastapi.HTTPBearer` / `HTTPBasic` / `APIKeyHeader` / `CookieAuth` / `unauthorized_error` (fastapi)
- Sentry 연동: `compose.fastapi.init_sentry` / `capture_error` / `create_before_send_hook` / `ErrorEvent` / `Level` (fastapi, sentry)
- Lambda 함수 호출: `compose.aws.LambdaClient` / `LambdaInvocationError` (aws)
- S3 오브젝트 저장소: `compose.aws.S3Store` (aws)
- S3 Presigned URL 생성: `compose.aws.S3UrlGenerator` (aws)
- S3 오브젝트 존재 확인: `compose.aws.s3_obj_exists` (aws)
- 트레이서/미터 프로바이더 설정: `compose.otel.get_default_tracer_provider` / `get_default_meter_provider` / `ServiceResourceAttrs` (otel)
- Loguru OpenTelemetry 계측: `compose.otel.LoguruInstrumentor` (otel)
- FastAPI 앱 계측: `compose.otel.instrument_app` (otel)
- Gunicorn 설정: `compose.gunicorn.GunicornSettings` / `export_settings`
- 테스트 유틸리티: `compose.testing` 모듈 (pytest)
- MongoDB 테스트 컨테이너: `compose.testcontainers.MongoDbContainer` (testcontainers)

### 유틸리티

- 비동기 작업 동시 실행: `compose.asyncio` 모듈
- 함수를 스레드 풀에서 실행: `compose.concurrent` 모듈
- 의존 관계 있는 작업을 DAG로 실행: `compose.dag` 모듈
- IO를 청크 단위로 읽기: `compose.stream` 모듈
- 이터레이터/옵셔널 유틸리티: `compose.func` 모듈
- UUID 생성, 서브클래스 탐색 등: `compose.utils` 모듈
- 시간/단위 상수: `compose.constants` 모듈
- 공통 타입 앨리어스: `compose.typing` 모듈 (`compose.tp`로도 접근 가능)

## 선택적 의존성

- `jwt` (`uv add pozalabs-compose[jwt]`): `auth.JWTDecoder` / `JWTIssuer`
- `oauth` (`uv add pozalabs-compose[oauth]`): `auth.AuthorizationServer`
- `aws` (`uv add pozalabs-compose[aws]`): `aws` 모듈 전체, `messaging.SqsMessageQueue`
- `dependency-injector` (`uv add pozalabs-compose[dependency-injector]`): `di.dependency_injector` 모듈
- `dishka` (`uv add pozalabs-compose[dishka]`): `di.dishka` 모듈
- `fastapi` (`uv add pozalabs-compose[fastapi]`): `fastapi` 모듈 전체
- `httpx` (`uv add pozalabs-compose[httpx]`): `httpx.HeaderAuth`
- `loguru` (`uv add pozalabs-compose[loguru]`): `logging` 모듈 전체
- `mongo` (`uv add pozalabs-compose[mongo]`): `repository.MongoRepository` / `MongoDocument` / `setup_indexes` / `finder` / `lister`, `query.MongoQuery` / `MongoPaginationQuery` / `MongoOffsetPaginationQuery` / `MongoCursorPaginationQuery`, `query.mongo.op`, `uow.MongoUnitOfWork` / `mongo_transactional`, `entity.MongoEntity`, `types.PyObjectId`, `lock.MongoLock` / `MongoLockAcquirer`
- `otel` (`uv add pozalabs-compose[otel]`): `otel` 모듈 전체 (`instrument_app`은 fastapi도 필요)
- `sentry` (`uv add pozalabs-compose[sentry]`): `fastapi.init_sentry` / `capture_error` / `create_before_send_hook` / `ErrorEvent` / `Level` (fastapi도 필요)
- `sql` (`uv add pozalabs-compose[sql]`): `entity.SQLEntity`, `repository.SQLRepository`, `uow.SQLUnitOfWork` / `sql_transactional`

extras가 아닌 선택적 의존성 (패키지를 직접 설치):

- `pytest`: `testing` 모듈
- `testcontainers[mongodb]`: `testcontainers` 모듈

## 추가 자료

- [인증 가이드](https://github.com/pozalabs/compose/blob/main/docs/auth-guide.md)
- [FastAPI/SQL 사용 예시](https://github.com/pozalabs/compose/blob/main/examples/)
- [변경 이력](https://github.com/pozalabs/compose/blob/main/CHANGELOG.md)
