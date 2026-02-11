# Compose 프로젝트 가이드

## Linear 연동

이슈 생성 시 아래 정보 사용

- area: compose
- team: 내부제품

## 코드 스타일

- 언어: 모든 문서와 커뮤니케이션은 한국어 사용

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

### 주의사항

- 테스트 실행 시 반드시 `tests` 폴더를 대상으로 지정 (examples 폴더와의 모듈명 충돌 방지)