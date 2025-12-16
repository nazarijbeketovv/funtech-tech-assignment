from typing import Any, Protocol


class MessageBrokerPublisherProtocol(Protocol):
    async def publish_new_order(self, payload: dict[str, Any]) -> None: ...
