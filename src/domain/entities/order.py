"""Доменная сущность заказа."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError
from domain.value_objects.order_status import OrderStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class Order:
    """Заказ как доменная сущность.

    Инварианты:
    - `total_price` > 0
    - список `items` не пустой

    Attributes:
        user_id: Идентификатор пользователя-владельца.
        items: Список товаров (JSON-совместимые структуры).
        total_price: Итоговая стоимость заказа.
        status: Текущий статус заказа.
        id: Идентификатор заказа (UUID).
        created_at: Время создания заказа (UTC).
    """

    user_id: int
    items: list[dict[str, Any]]
    total_price: Decimal
    status: OrderStatus = OrderStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Проверяет доменные инварианты после создания объекта.

        Raises:
            DomainValidationError: Если нарушены инварианты заказа.
        """
        if self.total_price <= Decimal("0"):
            raise DomainValidationError("Общая цена должна быть больше нуля.")
        if not self.items:
            raise DomainValidationError(
                "Заказ должен содержать как минимум один товар."
            )
