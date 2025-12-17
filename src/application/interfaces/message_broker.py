"""Контракт публикации сообщений в брокер.

Интерфейс абстрагирует конкретный брокер (Kafka/RabbitMQ и т.д.) от прикладных
сценариев.
"""

from typing import Any, Protocol


class MessageBrokerPublisherProtocol(Protocol):
    """Протокол издателя событий в брокер сообщений."""

    async def publish_new_order(self, payload: dict[str, Any]) -> None:
        """Публикует событие создания нового заказа.

        Args:
            payload: Данные события (в формате JSON-совместимого словаря).
        """
        ...
