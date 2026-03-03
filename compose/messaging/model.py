from typing import Any

from pydantic import SerializeAsAny, SkipValidation

from compose import model
from compose.event import Event


# body 필드의 타입 선언에 대한 배경:
#
# 이전에는 TypeVar("MessageBody", bound=Event)를 사용함. Generic을 상속하지 않는
# 클래스에서 TypeVar는 타입 체커에서 의미가 없고(pyrefly bad-argument-type 에러),
# Pydantic은 미해결 TypeVar를 Any로 취급하여 검증과 직렬화를 모두 건너뜀.
# 즉, 타입 안전성 없이 런타임에서만 우연히 동작하는 상태였음.
#
# 단순히 Event나 Event[Any]로 바꾸면 Pydantic이 Event 스키마로 검증하면서
# 하위 클래스 인스턴스를 Event로 변환하고(extra="ignore"로 추가 필드 제거),
# 직렬화 시에도 Event 스키마를 사용하여 하위 클래스의 커스텀 타입(PyObjectId 등)을
# 처리하지 못함.
#
# SkipValidation: 검증을 건너뛰어 하위 클래스 인스턴스를 그대로 보존
# SerializeAsAny: 선언 타입이 아닌 런타임 실제 타입의 직렬화기를 사용
class EventMessage(model.BaseModel):
    body: SerializeAsAny[SkipValidation[Event[Any]]]


class SqsEventMessage(EventMessage):
    receipt_handle: str
