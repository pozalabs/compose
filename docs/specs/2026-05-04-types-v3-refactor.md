# compose.types v3 리팩터링

## 목표

Pydantic v1 bridge를 제거하고 v2 네이티브 설계로 전환하여, 커스텀 타입 구현의 안전성과 단순성을 개선

## 상세

### 제거 대상

- `CoreSchemaGettable` 클래스
- `SupportsGetValidators` 프로토콜
- `chain()` 함수
- `get_pydantic_core_schema()` 헬퍼 함수
- `ValidatablePrimitive` 클래스
- `MARKER_IS_COMPOSE_VALIDATOR`, `MARKER_COMPOSE_VALIDATORS` 상수
- `caster()` 함수
- `TypedList`, `StrList`, `IntList`, `create_list_type()`, `_create_list_type()` (레거시)
- `helper.py` 파일
- `compose/typing.py`의 `Validator`, `ValidatorGenerator` 타입 별칭 (유일 사용처인 `primitive.py`의 `__get_validators__` 제거로 불필요)

### 새 구조

`primitive.py`가 `Str`, `Int`, `Float` 기본 클래스와 `@validator` 데코레이터를 제공:

```python
from compose.types import Str, Int, Float, List, validator
```

### 기본 클래스 설계

```python
class Str(str):
    _validators: ClassVar[list] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # MRO 역순 수집: base → derived 순서 보장
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if isinstance(member, classmethod)
               and getattr(member.__func__, '_is_validator', False)
        ]

    @classmethod
    def validated(cls, v, /):
        for fn in cls._validators:
            v = fn(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(
            source_type.validated, handler(str)
        )
```

`Int`, `Float`도 동일 구조. 각 클래스가 `__get_pydantic_core_schema__`에서 자신의 primitive 타입(`int`, `float`)을 직접 지정. 기존 `CoreSchemaGettable[T]`의 제네릭 추출 메커니즘 대신 세 클래스를 각각 정의.

### `@validator` 데코레이터

classmethod에 마커를 부여. `__init_subclass__`가 자동 수집:

```python
def validator(fn):
    fn._is_validator = True
    return fn
```

### validator 규약

- classmethod로 정의하고 `@validator`를 `@classmethod` 아래(안쪽)에 배치
- `cls`와 값을 받아 `Self`를 반환 (cls(v) 호출 허용)
- 검증 실패 시 예외 발생
- 변환이 필요하면 변환된 값으로 `cls(v)` 반환
- raw primitive를 반환해도 `validated()`의 마지막 `cls(v)`가 올바른 타입을 보장

```python
class BoardName(Str):
    @classmethod
    @validator
    def check_not_blank(cls, v: str) -> Self:
        if not v or v.isspace():
            raise ValueError("board name cannot be blank")
        return cls(v.strip())
```

데코레이터 순서 오용 감지: `@validator`가 classmethod descriptor가 아닌 일반 함수에 적용되었는지 확인하는 로직은 불필요. `__init_subclass__`가 `isinstance(member, classmethod)` 체크를 하므로, 순서가 잘못되면 해당 메서드가 수집되지 않아 silent failure가 아닌 "validator가 동작하지 않음"으로 나타남. 이는 테스트에서 즉시 발견됨.

### 생성 경로

- `cls(v)`: 검증 없이 인스턴스 생성 (신뢰 코드용, 내부 사용)
- `cls.validated(v)`: validator 체인 실행 후 `cls(v)`로 인스턴스 생성 (validator가 이미 `Self`를 반환해도 재래핑 — immutable이므로 무해)
- Pydantic 모델 필드: `validated`를 자동 호출

### 내부 제공 타입 정책

compose가 제공하는 타입(`Byte`, `Seconds`, `MilliSeconds`, `_S3ObjectUrl`)은 always-validated를 보장하기 위해 `__new__` 오버라이드를 유지. `_S3ObjectUrl`은 `__new__`에서 URL 정규화(키 추출, 경로 인코딩)를 수행하므로 `@validator`로 대체 불가:

```python
class Seconds(Float):
    def __new__(cls, v: Any, /) -> Self:
        v = super().__new__(cls, v)
        if v < 0:
            raise ValueError(f"`{cls.__name__}` must be a non-negative float")
        return v
```

사용자 코드에서는 `@validator` + `validated()` 패턴을 사용. `__new__` 오버라이드는 compose 내부 타입에만 허용.

`__new__` 오버라이드 타입을 상속하면서 `@validator`를 추가하는 것은 허용. 이 경우 validator의 `cls(v)` 호출과 `validated()` 마지막의 `cls(v)` 호출에서 `__new__` 검증이 두 번 실행되지만, immutable 타입이므로 무해.

### base 클래스 직접 사용

`Str`, `Int`, `Float`는 직접 사용 가능. `__init_subclass__`는 서브클래스에만 호출되므로 base 클래스의 `_validators`는 항상 `[]`. `Str.validated("hello")`는 validator 없이 `Str("hello")`를 반환 — 의도된 동작.

### `List` 타입

`ListMeta` 메타클래스 기반. `TypedList`, `StrList`, `IntList` 제거:

```python
class ListMeta(type):
    _cache: dict[str, type] = {}

    def __getitem__(cls, item):
        type_name = item.__name__ if hasattr(item, '__name__') else str(item)
        if (cached := cls._cache.get(type_name)) is not None:
            return cached

        element_type = item
        new_cls = type(
            f"{type_name.title()}List",
            (list,),
            {"__get_pydantic_core_schema__": classmethod(
                lambda c, source_type, handler, _et=element_type:
                    core_schema.no_info_after_validator_function(
                        source_type, handler(list[_et])
                    )
            )},
        )
        cls._cache[type_name] = new_cls
        return new_cls


class List(list, metaclass=ListMeta): ...
```

### `__init__.py` export 변경

제거:
- `CoreSchemaGettable`, `SupportsGetValidators`, `chain`, `get_pydantic_core_schema`
- `TypedList`, `StrList`, `IntList`

유지:
- `Str`, `Int`, `Float`, `List`, `validator`
- `Byte`, `DateTime`, `DateRange`, `Seconds`, `MilliSeconds`
- `MimeType`, `MimeTypeInfo`, `ContentDisposition`
- `create_s3_object_url`, `PyObjectId`

`DateTime`, `DateRange`는 primitive 서브클래스가 아니므로 (pendulum.DateTime, dataclass) 이번 변경에 영향 없음. `MimeType`은 `Str` 서브클래스이지만 validator 없이 factory method만 제공하므로 변경 불필요. `ContentDisposition`은 plain `str` 서브클래스(compose 타입 미사용)이므로 무관.

### 테스트 파일 처리

삭제:
- `test_validatable_primitive.py`: `ValidatablePrimitive` 제거로 테스트 대상 소멸
- `test_core_schema_gettable.py`: `CoreSchemaGettable` 제거로 테스트 대상 소멸
- `test_str_list.py`: `StrList` 제거로 테스트 대상 소멸
- `test_int_list.py`: `IntList` 제거로 테스트 대상 소멸

유지 (변경 불필요):
- `test_str.py`, `test_int.py`, `test_float.py`: base 타입의 Pydantic 통합 테스트. `Str`/`Int`/`Float`의 부모 클래스가 바뀌지만 외부 동작은 동일
- `test_list.py`: `List[T]` 동적 생성/캐싱 테스트. `ListMeta` 구현이 리팩터링되지만 동작은 동일
- `test_byte.py`, `test_seconds.py` 등 내부 제공 타입 테스트: `__new__` 오버라이드 유지이므로 변경 불필요

### 버전

Major 업데이트: `2.7.0` → `3.0.0`

## 경계

- 항상: validator는 classmethod + `@validator` 데코레이터로 정의
- 항상: 자동 체이닝 순서는 base → derived (MRO 역순)
- 항상: Pydantic 통합은 `validated` classmethod 경유
- 먼저: 외부 프로젝트 마이그레이션은 compose 3.0 배포 이후 별도 진행
- 절대: 사용자 코드에서 `__new__`를 직접 오버라이드하지 않음 (compose 내부 제공 타입만 always-validated 목적으로 허용)

## 검증

### 자동 검증

- `validated(v)` 호출 시 모든 validator가 base → derived 순서로 실행되는지
- 상속 체인에서 부모 validator 누락 없이 자동 수집되는지
- `cls(v)` 직접 호출이 validator를 실행하지 않는지
- Pydantic 모델 필드 역직렬화 시 `validated` 경유 검증이 동작하는지
- validator에서 `cls(v)` 호출 시 무한 루프 없이 인스턴스가 반환되는지
- `List[T]` 타입에서 element-level 검증이 Pydantic을 통해 정상 동작하는지

### 타입 체커

- `uv run pyrefly check`로 새 구조에서 타입 에러 없음 확인

### 이미 보장되는 것 (별도 검증 불필요)

- JSON 직렬화/역직렬화: Pydantic의 primitive 타입 직렬화가 기본 동작
- `List` 캐싱: 단순 dict 캐시이므로 identity 비교(`is`)로 충분
