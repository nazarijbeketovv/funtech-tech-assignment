from dataclasses import dataclass
from typing import Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.repositories import OrderRepositoryProtocol
from domain.entities.order import Order
from domain.value_objects.order_status import OrderStatus
from infra.db.models import OrderModel


@dataclass(slots=True, kw_only=True)
class OrderRepositorySQLAlchemy(OrderRepositoryProtocol):
    session: AsyncSession

    async def create(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            items=order.items,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity_required(model)

    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def update_status(
        self, order_id: UUID, status: OrderStatus
    ) -> Order | None:
        await self.session.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(status=status)
        )
        await self.session.flush()
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def list_by_user(self, user_id: int) -> list[Order]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_entity_required(model) for model in models]

    def _to_entity(self, model: OrderModel | None) -> Order | None:
        if model is None:
            return None
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=self._ensure_list(model.items),
            total_price=self._ensure_decimal(model.total_price),
            status=OrderStatus(model.status),
            created_at=model.created_at,
        )

    def _to_entity_required(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=self._ensure_list(model.items),
            total_price=self._ensure_decimal(model.total_price),
            status=OrderStatus(model.status),
            created_at=model.created_at,
        )

    def _ensure_list(self, items: Any) -> list[dict[str, Any]]:
        if isinstance(items, list):
            return items
        return []

    def _ensure_decimal(self, value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
