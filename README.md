# compose

Pozalabs 백엔드 서비스의 공통 컴포넌트 라이브러리

도메인 모델링부터 영속성, 메시징, API 통합까지, 서비스 구현에 반복되는 전술적 패턴을 제공

## 설계 원칙

- **DDD 빌딩 블록**: Entity, Repository, Command, Event, UoW 등 전술적 패턴을 일관된 인터페이스로 제공
- **선언형 조합**: 쿼리 연산자를 조합해 MongoDB 표현식을 만드는 Query DSL
- **코어 / 통합 분리**: 핵심 모듈은 프레임워크에 의존하지 않으며, FastAPI, AWS 등은 선택적 의존성으로 분리

## 문서

- [모듈 인덱스](compose/AGENTS.md)
- [인증 가이드](docs/auth-guide.md)
- [v2 마이그레이션 가이드](docs/v2-migration-guide.md)

## 시작하기

- Python 3.13+

```bash
uv add pozalabs-compose
```

도메인 모델링은 `compose.entity`와 `compose.repository`부터 시작하면 됨. 사용 예시는 `examples/` 참고

## 개발

```bash
# 테스트
uv run pytest tests -m unit
uv run pytest tests -m integration

# 타입 검사
uv run pyrefly check
```
