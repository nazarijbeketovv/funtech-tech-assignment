"""Маппер заказа для выдачи через API.

Преобразует `OrderDTO` из слоя application в Pydantic-схемы ответов.
"""

from application.dtos.order import OrderDTO
from api.v1.schemas import OrderResponseSchema


class OrderPresentationMapper:
    """Преобразователь DTO заказа в схемы ответа API."""

    def to_response(self, dto: OrderDTO) -> OrderResponseSchema:
        """Преобразует один DTO заказа в схему ответа.

        Args:
            dto: DTO заказа.

        Returns:
            OrderResponseSchema: Pydantic-схема ответа.
        """
        return OrderResponseSchema(
            id=dto.id,
            user_id=dto.user_id,
            items=dto.items,
            total_price=dto.total_price,
            status=dto.status,
            created_at=dto.created_at,
        )

    def to_list(self, dtos: list[OrderDTO]) -> list[OrderResponseSchema]:
        """Преобразует список DTO заказов в список схем ответа.

        Args:
            dtos: Список DTO заказов.

        Returns:
            list[OrderResponseSchema]: Список Pydantic-схем для ответа.
        """
        return [self.to_response(dto) for dto in dtos]
