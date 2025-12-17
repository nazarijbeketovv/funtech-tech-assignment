"""Мапперы доменных сущностей в DTO.

Функции модуля преобразуют сущности домена в DTO для использования на уровне
application (use cases) и API (presentation).
"""

from application.dtos.order import OrderDTO
from application.dtos.user import UserDTO
from domain.entities.order import Order
from domain.entities.user import User


def order_to_dto(order: Order) -> OrderDTO:
    """Преобразует доменную сущность заказа в DTO.

    Args:
        order: Доменная сущность заказа.

    Returns:
        OrderDTO: DTO заказа.
    """
    return OrderDTO(
        id=order.id,
        user_id=order.user_id,
        items=order.items,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
    )


def user_to_dto(user: User) -> UserDTO:
    """Преобразует доменную сущность пользователя в DTO.

    Args:
        user: Доменная сущность пользователя.

    Returns:
        UserDTO: DTO пользователя.

    Raises:
        ValueError: Если у пользователя отсутствует `id`.
    """
    if user.id is None:
        raise ValueError("У пользователя должен быть id для преобразования в DTO")
    return UserDTO(id=user.id, email=user.email, created_at=user.created_at)
