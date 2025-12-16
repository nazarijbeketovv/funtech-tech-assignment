from application.dtos.order import OrderDTO
from api.v1.schemas import OrderResponseSchema


class OrderPresentationMapper:
    def to_response(self, dto: OrderDTO) -> OrderResponseSchema:
        return OrderResponseSchema(
            id=dto.id,
            user_id=dto.user_id,
            items=dto.items,
            total_price=dto.total_price,
            status=dto.status,
            created_at=dto.created_at,
        )

    def to_list(self, dtos: list[OrderDTO]) -> list[OrderResponseSchema]:
        return [self.to_response(dto) for dto in dtos]
