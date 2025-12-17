"""Value object статуса заказа."""

from enum import Enum


class OrderStatus(str, Enum):
    """Статусы заказа.

    Attributes:
        PENDING: Заказ создан, но ещё не оплачен/не обработан.
        PAID: Заказ оплачен.
        SHIPPED: Заказ отправлен.
        CANCELED: Заказ отменён.
    """

    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"
