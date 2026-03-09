# compose.dishka 모듈

## 목표

dependency-injector의 명시적 와이어링으로 인한 연쇄 수정 문제를 해소하기 위해, dishka 기반 DI 통합 모듈을 compose에 별도로 제공한다. 기존 `compose.dependency`는 유지하고, 신규 프로젝트부터 `compose.dishka`를 적용하여 검증한다.

## 상세

### 모듈 구조

- `compose.fastapi.injected_route`: dishka 기반 auto-wiring route class 팩토리
- `compose.dependency`, `compose.fastapi`의 기존 DI 코드: 변경 없음
- dishka는 optional dependency로 추가 (기존 fastapi, otel 등과 동일 패턴)
- `compose.dishka` 모듈은 초기에 생성하지 않음. 향후 FastAPI 외 통합(EventBus 등)이 필요할 때 추가

### 패키지 통합 로드맵

단계적으로 `compose.di`로 통합한다:

1. 현재: `compose.fastapi`에 `injected_route` 추가, `compose.dependency` 유지
2. 검증 완료 후: `compose.di`로 통합, `compose.dependency`는 re-export로 하위호환 유지
3. 최종: dependency-injector 지원 종료 시 `compose.dependency` 제거

### 의존성 경계

정의 계층(Provider, Scope, @provide)은 compose가 래핑하지 않는다. 소비자가 dishka를 직접 의존한다.

```python
# 소비자 코드
import compose
from dishka import Provider, Scope, provide              # 정의 계층: dishka 직접 사용

compose.fastapi.injected_route(...)  # 사용 계층: compose 제공
```

### 공개 API

#### `injected_route(container)`

dishka의 `DishkaRoute`를 확장하여, 엔드포인트 파라미터 중 container가 해결 가능한 타입을 자동으로 `FromDishka[Type]`으로 변환하는 route class를 반환하는 팩토리.

- container에 등록된 구체 타입(`isinstance(type_hint, type)`)이면 변환 대상. 단, 어노테이션 없음, Any, Optional, Union, Annotated는 명시적으로 제외
- Generic, Protocol 타입은 초기에 지원하지 않음. 실제 필요성이 확인되면 추가
- 기본값이 있는 파라미터도 container 해결 가능 타입이면 변환 (기본값을 제거하여 dishka가 주입하도록 함)
- 시그니처 변환은 route 등록 시(`__init__`)에 수행
- 타입 충돌(여러 Provider에 동일 타입 등록)은 dishka에 위임

```python
import compose

from dishka import make_async_container

container = make_async_container(*providers)
router = APIRouter(route_class=compose.fastapi.injected_route(container))

@router.post("/playlists")
async def create_playlist(cmd: CreatePlaylist, handler: CreatePlaylistHandler):
    # cmd: FastAPI가 request body로 처리 (container가 해결할 수 없는 타입)
    # handler: dishka가 주입 (container가 해결 가능한 타입)
    return await handler.execute(cmd)
```

### 타입 판별 방식

container의 registry 체인을 순회하여 등록된 타입을 수집하고, 엔드포인트 파라미터의 타입이 이 집합에 포함되는지 판별한다.

- `container.registry`는 scope별 `Registry` 객체의 연결 리스트 (`child_registry`로 연결)
- 각 `Registry.factories`의 키가 `DependencyKey(type_hint, component, depth)` 객체이므로, `key.type_hint`를 수집하여 해결 가능한 타입 집합을 구성
- `AsyncContainer` 자체와 `type_hint=None`인 엔트리는 수집에서 제외
- 시그니처 변환 시 `__signature__`와 `__annotations__`를 모두 갱신해야 dishka의 `inject`가 `FromDishka` 어노테이션을 인식
- 위 속성들은 dishka의 공식 API가 아닌 내부 구현이므로, dishka 버전을 `>=1.9,<2` 범위로 고정하고 업그레이드 시 검증 필요

- container에서 해결 가능한 타입: `FromDishka[Type]`으로 변환
- 해결 불가능한 타입: 변환 없이 그대로 유지 (FastAPI가 request body, path param 등으로 처리)
- `FromDishka[Type]` 어노테이션은 dishka의 `@inject`에 의해 OpenAPI 스키마에서 자동으로 제외됨

### 앱 부트스트랩

소비자 프로젝트에서 dishka 컨테이너를 생성하고 FastAPI에 연결하는 코드는 compose가 래핑하지 않는다. `setup_dishka`와 `injected_route`를 함께 사용한다.

```python
import compose

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI

providers = [InfraProvider(), PlaylistProvider(), UserProvider()]
container = make_async_container(*providers)

router = APIRouter(
    route_class=compose.fastapi.injected_route(container),
    prefix="/playlists",
)

app = FastAPI()
app.include_router(router)
setup_dishka(container, app)
```

### 스크립트에서의 사용

스크립트에서는 `container.get(Type)`을 직접 호출한다. compose가 별도 래퍼를 제공하지 않는다.

```python
container = make_async_container(*providers)
handler = await container.get(CreatePlaylistHandler)
await handler.execute(cmd)
```

### 제공하지 않는 것

초기 버전에서 아래는 제공하지 않으며, 필요 시 추가한다:

- `resolve()` 래퍼 (dishka의 `container.get()`이 타입 기반 해결을 네이티브 지원)
- EventBus/MessageBus 연동
- `resolve_by_name()`, `resolve_by_object_name()` 등 이름 기반 해결

## 경계

- 항상: 기존 `compose.dependency` 코드를 변경하지 않는다
- 항상: 정의 계층은 dishka API를 직접 사용한다 (compose 래핑 없음)
- 항상: container가 해결할 수 없는 파라미터는 변환하지 않고 그대로 둔다
- 항상: container에 등록된 구체 타입이면 변환 대상. 어노테이션 없음, Any, Optional, Union, Annotated는 명시적 제외. Generic, Protocol은 초기 미지원
- 먼저: 기존 프로젝트 전환 전에 신규 프로젝트에서 충분히 검증한다
- 절대: dishka 통합 코드가 `compose.dependency`에 의존하지 않는다

## 검증

### 유닛 테스트

- container가 해결 가능한 타입만 `FromDishka[Type]`으로 변환하는지 확인
- container가 해결할 수 없는 타입(request body, path param 등)이 변환 없이 유지되는지 확인
- `injected_route`로 생성한 route class가 DishkaRoute를 확장하는지 확인
- 어노테이션이 없는 파라미터, Annotated/Optional/Union 타입이 변환 대상에서 제외되는지 확인
- 기본값이 있는 파라미터도 container 해결 가능 타입이면 변환되는지 확인

### 예제 검증

- `examples/fastapi_example`에서 로컬 `create_auto_wired_route` 대신 `compose.fastapi.injected_route`를 사용하도록 전환하여 실제 동작 확인
