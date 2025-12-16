from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError
from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class Order:
    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus = OrderStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.total_price <= Decimal("0"):
            raise DomainValidationError("Общая цена должна быть больше нуля.")
        if not self.items:
            raise DomainValidationError(
                "Заказ должен содержать как минимум один товар."
            )
