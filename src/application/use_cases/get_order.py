"""Use-case получения заказа с кешированием.

Сценарий пытается сначала отдать заказ из Redis (TTL управляется настройкой),
а при промахе — загружает из БД и обновляет кеш.
"""

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
    """Сценарий получения заказа по идентификатору (с кешем)."""

    uow: UnitOfWorkProtocol
    cache: CacheProtocol
    cache_ttl: int

    async def __call__(self, order_id: UUID, *, user_id: int) -> OrderDTO:
        """Возвращает заказ по `order_id`, проверяя владельца.

        Args:
            order_id: Идентификатор заказа.
            user_id: Идентификатор пользователя, запрашивающего заказ.

        Returns:
            OrderDTO: DTO заказа.

        Raises:
            OrderNotFoundError: Если заказ не найден или недоступен пользователю.
        """
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
            raise OrderNotFoundError("Заказ не найден")

        dto = order_to_dto(order)
        self._ensure_owner(dto, user_id=user_id)
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

    @staticmethod
    def _ensure_owner(dto: OrderDTO, *, user_id: int) -> None:
        """Проверяет, что заказ принадлежит пользователю.

        Args:
            dto: DTO заказа.
            user_id: Идентификатор пользователя.

        Raises:
            OrderNotFoundError: Если заказ принадлежит другому пользователю.
        """
        if dto.user_id != user_id:
            raise OrderNotFoundError("Заказ не найден")
