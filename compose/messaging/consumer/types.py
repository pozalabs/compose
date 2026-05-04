from typing import Protocol


class MessageConsumerType(Protocol):
    async def run(self) -> None: ...

    def shutdown(self) -> None: ...
