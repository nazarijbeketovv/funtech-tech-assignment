from datetime import datetime
from decimal import Decimal
from typing import Any, Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from domain.value_objects.order_status import OrderStatus


class OrderCreateSchema(BaseModel):
    items: list[dict[str, Any]] = Field(min_length=1)
    total_price: Annotated[
        Decimal,
        Field(gt=0, max_digits=10, decimal_places=2),
    ]


class OrderUpdateSchema(BaseModel):
    status: OrderStatus


class OrderResponseSchema(BaseModel):
    id: UUID
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
