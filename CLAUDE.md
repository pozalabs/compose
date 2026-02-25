# Compose 프로젝트 가이드

## Linear 연동

이슈 생성 시 아래 정보 사용

- area: compose
- team: 내부제품

## 에러 메시지

에러 메시지는 두 가지 기준을 충족해야 한다.

- **행동 가능성**: 에러를 본 개발자가 즉시 다음 행동을 할 수 있는가
  - 선택지가 있는 경우 유효한 값 목록을 포함
  - 형식 제약이 있는 경우 기대 형식을 안내
- **맥락 충분성**: 에러 발생 지점을 특정할 수 있는가
  - 대상 객체의 클래스명이나 식별자를 포함
  - "given container" 같은 모호한 표현 대신 구체적 정보 사용

스타일:
- 식별자(클래스명, 변수명)에는 백틱 사용: `` `base_url` must be set ``
- 일반 값에는 장식 없이 그대로 표기: `No provider named x for Foo`

## 타입 검사

```bash
uv run pyrefly check
```

- 설정: `pyproject.toml`의 `[tool.pyrefly]` 섹션

## 테스트

### 실행 방법

```bash
# unit 테스트 실행
uv run pytest tests -m unit

# integration 테스트 실행
uv run pytest tests -m integration

# 전체 테스트 실행
uv run pytest tests
```

### 마커

| 마커          | 용도     |
|-------------|--------|
| unit        | 단위 테스트 |
| integration | 통합 테스트 |

### 구조

- 모듈 레벨 함수로 작성 (클래스로 그룹핑하지 않음)
- 생성 실패 테스트 이름: `test_cannot_xxx` (e.g., `test_cannot_create_skip_with_negative`)

### 검증 방식

- 결과 검증 시 필드를 개별 비교하지 않고, 기대 객체를 생성하여 직접 비교

### 주의사항

- 테스트 실행 시 반드시 `tests` 폴더를 대상으로 지정 (examples 폴더와의 모듈명 충돌 방지)