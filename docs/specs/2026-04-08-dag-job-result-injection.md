# DAGJob 결과 주입

## 목표

DAGJob의 함수 시그니처를 `func(completed) -> T`로 변경하여, 선행 노드의 실행 결과를 후행 노드의 입력으로 자연스럽게 주입할 수 있게 함

## 상세

### 현재 구조

- `DAGJob`은 함수와 고정 인자를 생성 시점에 바인딩 (`functools.partial`과 동일)
- `DAGExecutor`는 실행 순서만 제어하고, 노드 간 결과 전달 경로 없음

### 변경 내용

`DAGJob`의 func 시그니처를 `Callable[P, T]`에서 `Callable[[dict[K, T]], T]`로 변경

- func는 `results: dict[K, T]`를 받아 결과를 반환. results에는 해당 job의 dependencies에 해당하는 키의 결과만 포함
- 고정 인자(`*args`, `**kwargs`)는 `DAGJob`에서 제거
- `DAGExecutor.execute()`는 submit 시 dependencies 키만 필터링한 딕셔너리를 func에 전달
- 타입 파라미터에서 `**P`(ParamSpec) 제거: `DAGJob[K, T]`, `DAGExecutor` 관련 메서드도 동일하게 변경

### 팩토리 메서드

`no_dependencies`를 고정 인자 편의 메서드로 변경

```python
@classmethod
def fixed(cls, key, func, *args, dependencies=None, **kwargs):
    return cls(key=key, dependencies=dependencies or set(), func=lambda _: func(*args, **kwargs))
```

- 의존성 결과를 사용하지 않는 job을 간결하게 생성
- 메서드명은 `no_dependencies` 대신 고정 인자 바인딩이라는 역할에 맞게 `fixed`로 변경
- `dependencies` 기본값 `set()`으로 의존성 없는 케이스에서 간결하게 사용 가능

### 마이그레이션

compose 내부:
- 기존 테스트 5개를 새 인터페이스에 맞게 수정

palette 소비처 3곳 (모두 고정 인자 패턴 → `fixed`로 전환 가능)

마이그레이션 가이드는 CHANGELOG에 작성

## 경계

- 항상: `completed` 딕셔너리는 해당 job의 모든 의존성이 완료된 상태에서만 전달
- 항상: 기존 테스트 커버리지 유지
- 절대: `DAGExecutor`의 실행 로직(의존성 해석, 병렬 실행, ready queue) 변경 없음

## 검증

- 기존 테스트를 새 인터페이스로 마이그레이션하여 동일 동작 확인
- 결과 주입 테스트 추가: 선행 노드의 결과를 후행 노드가 입력으로 사용하는 케이스
- `fixed` 팩토리 메서드 테스트

## Tasks

- T1: DAGJob/DAGExecutor 인터페이스 변경 및 기존 테스트 마이그레이션
- T2: 결과 주입 테스트 추가
  - blocked by: T1
- T3: fixed 팩토리 메서드 테스트 추가
  - blocked by: T1
- T4: CHANGELOG 마이그레이션 가이드 작성
  - blocked by: T1
