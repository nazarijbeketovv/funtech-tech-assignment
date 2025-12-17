"""Use-case создания заказа.

Сценарий:
- создаёт заказ в БД;
- пишет событие в outbox (для надёжной доставки);
- кеширует заказ в Redis;
- пытается сразу опубликовать событие `new_order` в брокер сообщений.
"""

import json
from dataclasses import dataclass
from uuid import UUID, uuid4

from loguru import logger

from application.dtos.order import CreateOrderDTO, OrderDTO
from application.interfaces.cache import CacheProtocol
from application.interfaces.message_broker import MessageBrokerPublisherProtocol
from application.interfaces.uow import UnitOfWorkProtocol
from application.mappers import order_to_dto
from domain.entities.outbox_event import OutboxEvent
from domain.entities.order import Order


@dataclass(slots=True, kw_only=True)
class CreateOrderUseCase:
    """Сценарий создания заказа."""

    uow: UnitOfWorkProtocol
    cache: CacheProtocol
    message_broker: MessageBrokerPublisherProtocol
    cache_ttl: int

    async def __call__(self, payload: CreateOrderDTO) -> OrderDTO:
        """Создаёт заказ и инициирует публикацию события.

        Args:
            payload: DTO с данными для создания заказа.

        Returns:
            OrderDTO: Созданный заказ в виде DTO.
        """
        order = Order(
            id=uuid4(),
            user_id=payload.user_id,
            items=payload.items,
            total_price=payload.total_price,
        )

        event_id = uuid4()
        outbox_payload = {
            "event": "new_order",
            "order_id": str(order.id),
            "user_id": order.user_id,
            "event_id": str(event_id),
        }

        async with self.uow:
            created = await self.uow.order_repo.create(order)
            event = await self.uow.outbox_repo.add(
                OutboxEvent(
                    id=event_id, event_type="new_order", payload=outbox_payload
                )
            )
            event_id = event.id
            await self.uow.commit()

        dto = order_to_dto(created)
        cache_key = self._cache_key(dto.id)
        await self.cache.set(cache_key, self._serialize(dto), ttl=self.cache_ttl)
        try:
            await self.message_broker.publish_new_order(outbox_payload)
            async with self.uow:
                await self.uow.outbox_repo.mark_processed(event_id)
                await self.uow.commit()
        except Exception as exc:
            logger.warning(
                "Не удалось опубликовать событие new_order; будет повтор через outbox",
                extra={"error": str(exc), "event_id": str(event_id)},
            )
        return dto

    def _cache_key(self, order_id: UUID) -> str:
        """Формирует ключ кеша для заказа.

        Args:
            order_id: Идентификатор заказа.

        Returns:
            str: Ключ кеша.
        """
        return f"order:{order_id}"

    def _serialize(self, dto: OrderDTO) -> str:
        """Сериализует DTO заказа в JSON-строку для кеша.

        Args:
            dto: DTO заказа.

        Returns:
            str: JSON-строка.
        """
        return json.dumps(
            {
                "id": str(dto.id),
                "user_id": dto.user_id,
                "items": dto.items,
                "total_price": str(dto.total_price),
                "status": dto.status.value,
                "created_at": dto.created_at.isoformat(),
            }
        )
