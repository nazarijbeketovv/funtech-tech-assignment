"""Use-case обновления статуса заказа.

Сценарий обновляет статус заказа в БД с проверкой владельца и синхронно
обновляет запись в кеше.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from application.dtos.order import OrderDTO, UpdateOrderStatusDTO
from application.exceptions import OrderNotFoundError
from application.interfaces.cache import CacheProtocol
from application.interfaces.uow import UnitOfWorkProtocol
from application.mappers import order_to_dto
from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, kw_only=True)
class UpdateOrderStatusUseCase:
    """Сценарий обновления статуса заказа."""

    uow: UnitOfWorkProtocol
    cache: CacheProtocol
    cache_ttl: int

    async def __call__(self, payload: UpdateOrderStatusDTO) -> OrderDTO:
        """Обновляет статус заказа.

        Args:
            payload: DTO с идентификатором заказа, новым статусом и владельцем.

        Returns:
            OrderDTO: Обновлённый заказ.

        Raises:
            OrderNotFoundError: Если заказ не найден или не принадлежит пользователю.
        """
        async with self.uow:
            existing = await self.uow.order_repo.get_by_id(payload.order_id)
            if existing is None:
                raise OrderNotFoundError("Заказ не найден")
            if existing.user_id != payload.user_id:
                raise OrderNotFoundError("Заказ не найден")

            order = await self.uow.order_repo.update_status(
                payload.order_id, payload.status
            )
            if order is None:
                raise OrderNotFoundError("Заказ не найден")
            await self.uow.commit()

        dto = order_to_dto(order)
        cache_key = self._cache_key(payload.order_id)
        await self.cache.set(cache_key, self._serialize(dto), ttl=self.cache_ttl)
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

    def _deserialize(self, data: str) -> OrderDTO:
        """Десериализует JSON-строку из кеша в DTO заказа.

        Примечание: метод оставлен для симметрии и возможного расширения.

        Args:
            data: JSON-строка.

        Returns:
            OrderDTO: DTO заказа.
        """
        raw = json.loads(data)
        return OrderDTO(
            id=UUID(raw["id"]),
            user_id=raw["user_id"],
            items=raw["items"],
            total_price=Decimal(str(raw["total_price"])),
            status=OrderStatus(raw["status"]),
            created_at=datetime.fromisoformat(raw["created_at"]),
        )
