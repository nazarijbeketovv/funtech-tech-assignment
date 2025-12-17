"""DTO для заказов."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, kw_only=True)
class OrderDTO:
    """DTO заказа, используемый на уровне application/API.

    Attributes:
        id: Идентификатор заказа.
        user_id: Идентификатор владельца заказа.
        items: Список товаров (произвольные структуры).
        total_price: Итоговая стоимость.
        status: Статус заказа.
        created_at: Дата и время создания.
    """

    id: UUID
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class CreateOrderDTO:
    """DTO для создания заказа.

    Attributes:
        user_id: Идентификатор владельца заказа.
        items: Список товаров.
        total_price: Итоговая стоимость.
    """

    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal


@dataclass(slots=True, kw_only=True)
class UpdateOrderStatusDTO:
    """DTO для обновления статуса заказа.

    Attributes:
        order_id: Идентификатор заказа.
        status: Новый статус.
        user_id: Идентификатор владельца (для проверки прав).
    """

    order_id: UUID
    status: OrderStatus
    user_id: int
