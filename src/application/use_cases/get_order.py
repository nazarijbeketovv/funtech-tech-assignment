import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from json import JSONDecodeError

from application.dtos.order import OrderDTO
from application.exceptions import OrderNotFoundError
from application.mappers import order_to_dto
from application.interfaces.cache import CacheProtocol
from application.interfaces.uow import UnitOfWorkProtocol
from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, kw_only=True)
class GetOrderUseCase:
    uow: UnitOfWorkProtocol
    cache: CacheProtocol
    cache_ttl: int

    async def __call__(self, order_id: UUID, *, user_id: int) -> OrderDTO:
        cache_key = self._cache_key(order_id)
        cached = await self.cache.get(cache_key)
        if cached:
            try:
                dto = self._deserialize(cached)
                self._ensure_owner(dto, user_id=user_id)
                return dto
            except (JSONDecodeError, KeyError, ValueError, TypeError):
                await self.cache.delete(cache_key)

        async with self.uow:
            order = await self.uow.order_repo.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")

        dto = order_to_dto(order)
        self._ensure_owner(dto, user_id=user_id)
        await self.cache.set(cache_key, self._serialize(dto), ttl=self.cache_ttl)
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

    def _deserialize(self, data: str) -> OrderDTO:
        raw = json.loads(data)
        return OrderDTO(
            id=UUID(raw["id"]),
            user_id=raw["user_id"],
            items=raw["items"],
            total_price=Decimal(str(raw["total_price"])),
            status=OrderStatus(raw["status"]),
            created_at=datetime.fromisoformat(raw["created_at"]),
        )

    @staticmethod
    def _ensure_owner(dto: OrderDTO, *, user_id: int) -> None:
        if dto.user_id != user_id:
            raise OrderNotFoundError("Order not found")
