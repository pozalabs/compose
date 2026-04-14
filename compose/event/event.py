import uuid

from pydantic import ConfigDict, Field

from .. import field, model, types


# polymorphic_serialization: Event 타입으로 선언된 필드에서 하위 클래스 인스턴스가
# 담길 때, 선언 타입이 아닌 런타임 실제 타입의 필드까지 직렬화되도록 함.
# 이 설정은 참조되는 타입(Event)에 있어야 동작함.
class Event(model.BaseModel):
    model_config = ConfigDict(polymorphic_serialization=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    published_at: types.DateTime = field.DateTimeField()
