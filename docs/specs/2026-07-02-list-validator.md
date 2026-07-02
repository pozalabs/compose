# List 타입 validator 지원

## 목표

`Str`/`Int`/`Float`와 동일한 validator 메커니즘을 `List` 타입에 추가하여, 서브클래스에서 리스트 전체에 대한 검증과 변환을 선언적으로 정의할 수 있게 함

## 상세

### 현재 구조

`Str`/`Int`/`Float`는 다음 세 요소로 validator를 지원:

- `__init_subclass__`: MRO를 순회하며 `@validator`로 마킹된 classmethod를 `_validators`에 수집
- `validated(cls, v) -> Self`: `_validators` 체인을 실행하고 `cls(v)`로 최종 인스턴스 반환
- `__get_pydantic_core_schema__`: `source_type.validated`를 after-validator로 등록

`List`는 현재 `__get_pydantic_core_schema__`만 있고 validator 메커니즘이 없음

### 변경 내용

`List` 클래스에 `__init_subclass__`, `validated`를 추가하고 `__get_pydantic_core_schema__`에서 `validated`를 after-validator로 연결

변경 후 시그니처:

```python
class List[T](list[T]):
    if TYPE_CHECKING:
        _validators: ClassVar[Validators]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for type_ in reversed(cls.__mro__)
            for member in type_.__dict__.values()
            if _is_compose_validator(member)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for func in cls._validators:
            v = func(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        args = get_args(source_type)
        if not args:
            for base in getattr(source_type, "__orig_bases__", ()):
                args = get_args(base)
                if args:
                    break
        if args:
            return _get_pydantic_core_schema(source_type.validated, handler(list[args[0]]))
        return _get_pydantic_core_schema(source_type.validated, handler(list))
```

### 호출 흐름

pydantic이 `List` 서브클래스를 역직렬화할 때:

1. pydantic이 내부 스키마(`list[T]`)로 개별 항목을 먼저 검증/변환
2. after-validator로 등록된 `validated`가 호출됨
3. `validated`가 `_validators` 체인을 순서대로 실행 (base -> derived)
4. 최종 결과를 `cls(v)`로 감싸 반환

validator가 없는 `List` 서브클래스는 `_validators`가 빈 리스트이므로 `cls(v)`만 실행되어 기존 동작과 동일

### 변경 대상

- `compose/types/primitive.py`: `List` 클래스에 `__init_subclass__`, `validated` 추가, `__get_pydantic_core_schema__`에서 `source_type` 대신 `source_type.validated` 사용
- `tests/types/unit/test_list.py`: validator를 사용하는 `List` 서브클래스 테스트 추가

## 경계

- 항상: `Str`/`Int`/`Float`의 validator 패턴과 동일한 인터페이스 유지
- 항상: 기존 `List` 서브클래스(`CustomStrList`, `NonBlankList` 등)의 동작이 변하지 않음을 보장
- 절대: 개별 항목 검증 로직을 List validator에 추가하지 않음 (항목 검증은 타입 파라미터 T의 책임)

## 검증

위험 지점: `__get_pydantic_core_schema__`에서 `source_type`을 `source_type.validated`로 바꾸는 것이 validator가 없는 기존 서브클래스의 동작을 깨뜨릴 수 있음

- 기존 `test_list.py` 테스트가 모두 통과하는지 확인 (validator 없는 서브클래스의 회귀 방지)
- List validator를 통한 검증: validator가 값을 거부할 때 `ValueError`가 발생하고 pydantic `ValidationError`로 전파되는지 확인
- List validator를 통한 변환: validator가 리스트를 변환한 결과가 최종 인스턴스에 반영되는지 확인
- validator 상속: base -> derived 순서로 validator가 실행되는지 확인 (Str의 `test_inherit_validators_in_base_to_derived_order`와 동일한 속성)
