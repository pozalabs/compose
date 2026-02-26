# 공개 API 네이밍 검토

## 맥락

- compose 패키지의 공개 API 중 의도를 잘 드러내지 않거나 일관성이 부족한 부분을 검토
- 대상: 모듈 `__init__.py`에서 `__all__`로 노출되는 심볼

## 발견 사항

### 1. `messaging` - Event와 Message 용어 혼용

하나의 메시징 흐름에서 두 접두사가 혼재:

- Event 계열: `EventMessage`, `SqsEventMessage`, `EventPublisher`, `EventHandler`(Protocol), `event_store`
- Message 계열: `MessageQueue`, `LocalMessageQueue`, `SqsMessageQueue`, `MessageConsumer`, `MessageBus`

실제 흐름:
1. `EventPublisher`가 `Event`를 `EventMessage`로 래핑하여 `MessageQueue`에 푸시
2. `MessageConsumer`가 `MessageQueue`에서 꺼내 `MessageBus`에 전달
3. `MessageBus`가 `Event` 클래스명으로 `EventHandler`를 찾아 위임

`MessageBus`는 내부적으로 `Event` 클래스명으로 핸들러를 매칭하고 `EventHandler.handle(evt: Event)`를 호출하므로, 실질적으로 Event Bus인데 이름이 `MessageBus`임.

### 2. `asyncio` vs `concurrent` - 동일 개념에 다른 파라미터명과 타입

| 개념 | `asyncio` | `concurrent` |
|---|---|---|
| 병렬 상한 | `concurrency: int` | `max_workers: int` |
| 타임아웃 | `timeout: float \| None` | `timeout: int \| None` |
| Job 클래스 | `AsyncJob` | `ThreadPoolJob` |
| Executor 클래스 | `AsyncTaskExecutor` | `ThreadPoolExecutor` |

- 같은 의미의 파라미터가 `concurrency`와 `max_workers`로 다름
- 타임아웃 타입이 한쪽은 `float`, 한쪽은 `int`
- Executor 이름이 한쪽은 `*Task*Executor`, 한쪽은 `*Executor`

### 3. `fastapi.param` - `as_query`와 `to_query` 구분 불명확

```python
def to_query(q):    # BaseModel을 Query 파라미터가 적용된 새 모델로 변환
def as_query(q):    # Depends(to_query(q)) 래핑
```

`to_X`와 `as_X`는 Python에서 보통 같은 변환의 뉘앙스 차이로 쓰이기 때문에, 이름만으로는 "모델 변환"과 "FastAPI 의존성 래핑"의 차이를 알 수 없음.

### 4. `types.List` - builtin 섀도잉

```python
class List[T](list[T], metaclass=ListMeta): ...
```

`from compose.types import List` 시 Python builtin `list`/`typing.List`와 혼동 가능. `TypedList` 팩토리가 이미 존재하므로, `List[str]` 문법 지원이 목적이라면 그 의도가 이름에 드러나지 않음.

### 5. `messaging.queue.local` - `event_store` 이름과 역할 불일치

```python
event_store: contextvars.ContextVar[EventMessageQueue] = contextvars.ContextVar("event_store")
```

"event store"는 이벤트 소싱의 Event Store를 연상시키지만, 실제로는 요청 스코프의 `EventMessage` 임시 대기열(deque)을 담는 ContextVar. "store"보다 "buffer"나 "queue"가 실제 역할에 가까움.

### 6. `field` - `IdField`/`DateTimeField`가 팩토리인데 필드처럼 보임

```python
IdField: Callable[..., Any] = _IdField()
DateTimeField: Callable[..., types.DateTime] = _DatetimeField()
```

사용 시 `id: PyObjectId = IdField()`처럼 호출해야 하므로 실질적으로 Field 팩토리. 하지만 이름이 `IdField`이므로 값 자체가 필드인 것처럼 보여 `id: PyObjectId = IdField` 같은 실수 유발 가능.

### 7. `fastapi.otel` - `NonInstrumentedUrls` 부정형 이름

```python
class NonInstrumentedUrls(list[str]):
    @classmethod
    def register(cls, *urls): ...
```

"계측하지 않을 URL 목록"이라는 의미. 부정형이라 `register`와 조합하면 이중 부정에 가까운 인지 비용 발생. 긍정형(`ExcludedUrls`, `InstrumentationExcludes`)이 의도를 더 명확히 드러냄.

### 8. `fastapi.param` - `WithPath`가 전치사구

```python
class WithPath:
    @classmethod
    def object_id(cls, path=None) -> tuple[type[PyObjectId], Path]: ...
    @classmethod
    def int(cls, path=None) -> tuple[type[int], Path]: ...
```

Path 파라미터 타입 튜플을 생성하는 정적 팩토리인데, 전치사구 이름은 "무엇이 Path를 가진다"와 "Path를 가지고 무엇을 한다" 사이에서 모호함. `PathParam`이나 `PathType` 같은 명사형이 더 명확함.

### 9. `fastapi.depends` - `CommandUpdater`와 `UserInjector` 네이밍 패턴 불일치

```python
class CommandUpdater[T, U]:     # 동사+명사 (커맨드를 업데이트하는 것)
class UserInjector[T, U]:       # 명사+명사 (유저를 주입하는 것)
```

같은 역할 그룹인데 네이밍 패턴이 다름. `UserInjector`가 `CommandUpdater`를 감싸는 상위 계층인데, 이름만으로는 관계가 보이지 않음.

## 우선순위

- 높음: 1(messaging 용어 혼용), 2(asyncio/concurrent 파라미터 불일치)
- 중간: 3(as_query/to_query), 4(List 섀도잉), 5(event_store)
- 낮음: 6(IdField), 7(NonInstrumentedUrls), 8(WithPath), 9(CommandUpdater/UserInjector)
