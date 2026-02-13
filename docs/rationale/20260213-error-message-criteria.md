# 에러 메시지 개선 판단 기준

## 맥락

- `compose/dependency/wiring.py`의 `resolve()` 에러 메시지를 개선하면서 적용한 기준 정리

## 결정

에러 메시지 품질을 두 가지 기준으로 평가한다.

### 1. 행동 가능성 (Actionable)

에러를 본 개발자가 즉시 다음 행동을 할 수 있는가.

- Bad: `Cannot find provider named 'x' for Foo from given container` → 유효한 name을 알 수 없어 코드를 뒤져야 함
- Good: `No provider named x for Foo. Available: ['a', 'b']` → 유효한 name을 바로 확인 가능

### 2. 맥락 충분성 (Context)

에러 발생 지점을 특정할 수 있는가.

- Bad: `Cannot find Foo from given container` → 어떤 컨테이너인지 불명
- Good: `No provider found for Foo in <ApplicationContainer>` → 어떤 컨테이너에서 실패했는지 명시

### 적용하지 않는 경우

두 기준이 이미 충족된 메시지는 변경하지 않는다. 예: `"Only class can be resolved"` — 입력값 검증이라 맥락이 자명하고, 행동(클래스를 넘기면 됨)이 메시지에 이미 담겨 있음.
