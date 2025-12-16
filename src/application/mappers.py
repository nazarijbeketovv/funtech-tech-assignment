from application.dtos.order import OrderDTO
from application.dtos.user import UserDTO
from domain.entities.order import Order
from domain.entities.user import User


def order_to_dto(order: Order) -> OrderDTO:
    return OrderDTO(
        id=order.id,
        user_id=order.user_id,
        items=order.items,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
    )


def user_to_dto(user: User) -> UserDTO:
    if user.id is None:
        raise ValueError("User must have an id to map to DTO")
    return UserDTO(id=user.id, email=user.email, created_at=user.created_at)
