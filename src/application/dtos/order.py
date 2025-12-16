from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, kw_only=True)
class OrderDTO:
    id: UUID
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class CreateOrderDTO:
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal


@dataclass(slots=True, kw_only=True)
class UpdateOrderStatusDTO:
    order_id: UUID
    status: OrderStatus
    user_id: int
