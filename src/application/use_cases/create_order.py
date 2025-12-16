import json
import logging
from dataclasses import dataclass
from uuid import uuid4, UUID

from application.dtos.order import CreateOrderDTO, OrderDTO
from application.mappers import order_to_dto
from application.interfaces.cache import CacheProtocol
from application.interfaces.message_broker import (
    MessageBrokerPublisherProtocol,
)
from application.interfaces.uow import UnitOfWorkProtocol
from domain.entities.outbox_event import OutboxEvent
from domain.entities.order import Order

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class CreateOrderUseCase:
    uow: UnitOfWorkProtocol
    cache: CacheProtocol
    message_broker: MessageBrokerPublisherProtocol
    cache_ttl: int

    async def __call__(self, payload: CreateOrderDTO) -> OrderDTO:
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
                "Failed to publish new_order event; will retry via outbox",
                extra={"error": str(exc), "event_id": str(event_id)},
            )
        return dto

    def _cache_key(self, order_id: UUID) -> str:
        return f"order:{order_id}"

    def _serialize(self, dto: OrderDTO) -> str:
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
