# compose

POZAlabs 백엔드 서비스의 공통 컴포넌트 라이브러리.

도메인 모델링부터 영속성, 메시징, API 통합까지 — 서비스 구현에 반복되는 전술적 패턴을 제공한다.

## 설계 원칙

- **DDD 빌딩 블록**: Entity, Repository, Command, Event, UoW 등 전술적 패턴을 일관된 인터페이스로 제공
- **선언형 조합**: 쿼리 연산자를 조합해 MongoDB 표현식을 만드는 Query DSL
- **코어 / 통합 분리**: 핵심 모듈은 프레임워크에 의존하지 않으며, FastAPI·AWS 등은 선택적 의존성으로 분리

## 구조

### 도메인 모델링

서비스의 도메인 개념을 표현하는 기반 타입과 패턴

- `entity` — 식별자와 생명주기를 가진 도메인 엔티티
- `command` — 도메인 명령 객체
- `event` — 도메인 이벤트
- `types` — 검증이 포함된 도메인 타입 (문자열, 숫자, 날짜, 바이트 등)
- `exceptions` — 행동 가능한 에러 계층 구조

### 영속성

도메인 객체의 저장과 조회

- `repository` — 저장소 패턴 (MongoDB, SQL)
- `query` — MongoDB Query DSL (연산자 → 스테이지 → 파이프라인 조합)
- `uow` — Unit of Work (트랜잭션 경계 관리)

### 메시징

도메인 이벤트의 발행과 소비

- `messaging` — MessageBus, EventPublisher, MessageConsumer, 큐 추상화

### 인프라

서비스 운영에 필요한 횡단 관심사

- `dependency` — 의존성 주입 컨테이너
- `auth` — JWT 발급/검증, OAuth 2.0
- `schema` — API 응답 모델, 페이지네이션
- `settings` — AWS Parameter Store 기반 설정

### 프레임워크 통합 (선택적 의존성)

설치된 경우에만 활성화되는 통합 모듈

- `fastapi` — 라우터, 예외 핸들러, 인증 스킴, Sentry
- `aws` — S3 URL 생성
- `opentelemetry` — 계측 확장
- `testcontainers` — 테스트용 Docker 컨테이너

## 시작하기

```bash
uv add pozalabs-compose
```

도메인 모델링은 `compose.entity`와 `compose.repository`부터 시작하면 된다. 사용 예시는 `examples/`를 참고.

## 선택적 의존성

extras 패키지는 관리하지 않는다. 아래 기능이 필요하면 해당 패키지를 직접 설치해야 한다.

- `pymongo` — MongoDB 지원 (`repository.mongo`, `query.mongo`, `uow.mongo`, `entity.MongoEntity`, `types.PyObjectId`, `lock.mongo`)
- `sqlalchemy` — SQL 지원 (`repository.sql`, `uow.sql`, `entity.SQLEntity`)
- `fastapi` — FastAPI 통합 (`fastapi`)
- `sentry-sdk` — Sentry 연동 (`fastapi` 내 Sentry 헬퍼)
- `loguru` — 구조화 로깅 (`logging`)
- `boto3` — AWS 서비스 (`aws`, `messaging.SqsMessageQueue`, `settings.AWSParameterStoreSettingsSource`)
- `httpx` — HTTP 클라이언트 확장 (`httpx`)
- `bcrypt` — 비밀번호 해싱 (`auth.HashedPassword`)
- `opentelemetry-distro[otlp]` — OpenTelemetry 계측 (`opentelemetry`)
- `pytest` — 테스트 유틸리티 (`testing`)
- `testcontainers[mongodb]` — 테스트용 MongoDB 컨테이너 (`testcontainers`)

## 개발

```bash
# 테스트
uv run pytest tests -m unit
uv run pytest tests -m integration

# 타입 검사
uv run pyrefly check
```
