# MessageQueue 제네릭 타입 파라미터 도입

## 목표

`SqsMessageQueue`의 `push`/`delete` 메서드가 파라미터 타입을 `SqsEventMessage`로 좁혀 발생하는 `bad-override` 타입 에러를 해소하고, push(발행)와 peek/delete(소비) 경로의 타입 요구 차이를 설계에 반영

## 상세

### 배경: push와 peek/delete의 비대칭

`SqsMessageQueue`에서 세 메서드의 타입 요구가 다름:

- `push`: `message.body`만 사용. `EventMessage`로 충분
- `peek`: SQS 응답에서 `receipt_handle`을 포함한 `SqsEventMessage`를 생성하여 반환
- `delete`: `receipt_handle`이 필요하므로 `SqsEventMessage` 필수

소비자 프로젝트(eapy-be, dio-backoffice)에서 `SqsMessageQueue` 인스턴스를 `EventPublisher`와 `MessageConsumer` 양쪽에 주입하고 있으므로, 단일 제네릭 파라미터로 세 메서드를 통일하면 invariance 문제가 발생. push를 제네릭 바깥에 두고 peek/delete만 파라미터화하여 해결

### MessageQueue 제네릭화

`MessageQueue`에 메시지 타입 파라미터 `M`을 도입하되, `push`는 항상 `EventMessage`를 받는다.

```python
class MessageQueue[M: EventMessage = EventMessage](abc.ABC):
    @abc.abstractmethod
    def push(self, message: EventMessage) -> None: ...

    @abc.abstractmethod
    def peek(self) -> M | None: ...

    @abc.abstractmethod
    def delete(self, message: M) -> None: ...
```

- bound: `EventMessage`
- default: `EventMessage` (파라미터 생략 시 기존 동작과 동일)
- `push`는 `M`이 아닌 `EventMessage`를 받음. SQS push에서 `receipt_handle`이 불필요하고, `EventPublisher`가 항상 `EventMessage(body=evt)`를 생성하므로 올바른 설계

`SqsMessageQueue(MessageQueue[SqsEventMessage])` 적용 후:

- `push(EventMessage)`: 기반 클래스와 동일, bad-override 해소
- `peek() -> SqsEventMessage | None`: M=SqsEventMessage, 공변 반환
- `delete(SqsEventMessage)`: M=SqsEventMessage, 기반 클래스와 일치

### EventPublisher에 MessagePushable Protocol 도입

`EventPublisher`는 `push`만 호출하므로 `MessageQueue[M]` 전체가 아닌 push 능력만 요구하면 됨. Protocol을 도입하여 invariance 문제를 회피한다.

```python
class MessagePushable(Protocol):
    def push(self, message: EventMessage) -> None: ...

class EventPublisher:
    def __init__(self, message_queue: MessagePushable):
        self.message_queue = message_queue

    def publish(self, evt: Event) -> None:
        self.message_queue.push(EventMessage(body=evt))
```

- `MessageQueue[M]`의 `push(EventMessage)`는 M에 무관하므로, 모든 `MessageQueue[M]`이 `MessagePushable`을 만족
- `SqsMessageQueue`를 `EventPublisher`에 전달할 수 있음 (eapy-be, dio-backoffice 패턴 유지)
- `MessagePushable`은 `publisher.py`에 정의하고, `messaging/__init__.py`에서 re-export

### MessageConsumer 제네릭화

`MessageConsumer`도 제네릭으로 만들어 `SqsMessageQueue`를 타입 안전하게 전달할 수 있도록 한다.

```python
class MessageConsumer[M: EventMessage = EventMessage]:
    def __init__(
        self,
        event_bus: EventBus,
        message_queue: MessageQueue[M],
        ...
    ): ...

    async def run(self) -> None:
        ...
        message = self.message_queue.peek()  # M | None
        await self.consume(message)           # M을 그대로 전달
        ...

    async def consume(self, message: M) -> None:
        await self.event_bus.handle_event(message.body)  # M: EventMessage이므로 body 접근 보장
        self.message_queue.delete(message)                # delete(M)
```

`run()` 내부의 `peek() -> consume() -> delete()` 체인에서 `M` 타입이 자연스럽게 흐른다.

소비자 프로젝트에서 `MessageConsumer(message_queue=sqs_queue)`로 호출하면 타입 체커가 `sqs_queue: MessageQueue[SqsEventMessage]`에서 `M=SqsEventMessage`를 추론하므로, 소비자 코드 변경 불필요.

### MessageConsumerType 프로토콜에서 consume 제거

`MessageConsumerType`은 `ThreadMessageConsumerRunner`와 `FastAPIMessageConsumerRunner`에서 사용되며, 두 러너 모두 `run()`과 `shutdown()`만 호출한다. `consume()`은 `run()` 내부에서 호출되는 구현 세부사항이므로 프로토콜에서 제거한다.

```python
class MessageConsumerType(Protocol):
    async def run(self) -> None: ...
    def shutdown(self) -> None: ...
```

### 변경 불필요한 영역

- `consumer/hook.py`: `HookArgType = str | EventMessage | Exception`에서 `M: EventMessage`이므로 `EventMessage`에 할당 가능
- `consumer_runner.py`: `run()`/`shutdown()`만 사용
- `model.py`: `EventMessage`, `SqsEventMessage` 정의 자체는 변경 없음

### 테스트 변경

- `test_event_publisher_publish.py`의 `InMemoryMessageQueue`: `push` 시그니처를 `EventMessage`로 맞춤 (현재와 동일)
- `test_message_consumer.py`의 `FakeMessageQueue`: 동일 (M=EventMessage, default)
- `test_fastapi_message_consumer_runner.py`의 `FakeMessageConsumer`: `consume` 메서드 삭제 (프로토콜에서 제거되어 불필요)

## 경계

- 항상: PEP 695 스타일, default 파라미터로 기존 코드 호환성 유지
- 절대: 런타임 동작 변경 없음, Hook 타입이나 EventBus 인터페이스는 건드리지 않음

## 검증

타입 체커(`pyrefly`)가 이미 보장하는 범위:

- 제네릭 파라미터의 bound 위반
- 오버라이드 시그니처 불일치 (`bad-override`)
- 메서드 호출 시 인자 타입 불일치

추가 자동화 검증이 필요하지 않음. 변경이 타입 힌트 수준에 한정되어 런타임 동작이 동일하고, 기존 테스트가 동작을 이미 커버하고 있으며, 타입 정합성은 `uv run pyrefly check`로 검증 가능
