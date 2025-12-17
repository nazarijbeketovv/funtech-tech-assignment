"""Pydantic-схемы для работы с заказами.

Схемы используются для валидации входящих данных и формирования ответов API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from domain.value_objects.order_status import OrderStatus


class OrderCreateSchema(BaseModel):
    """Схема запроса на создание заказа."""

    items: list[dict[str, Any]] = Field(min_length=1)
    total_price: Annotated[
        Decimal,
        Field(gt=0, max_digits=10, decimal_places=2),
    ]


class OrderUpdateSchema(BaseModel):
    """Схема запроса на обновление статуса заказа."""

    status: OrderStatus


class OrderResponseSchema(BaseModel):
    """Схема ответа с данными заказа."""

    id: UUID
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
