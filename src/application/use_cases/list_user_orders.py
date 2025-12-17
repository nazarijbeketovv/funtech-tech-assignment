"""Use-case получения списка заказов пользователя."""

from dataclasses import dataclass

from application.dtos.order import OrderDTO
from application.interfaces.uow import UnitOfWorkProtocol
from application.mappers import order_to_dto


@dataclass(slots=True, kw_only=True)
class ListUserOrdersUseCase:
    """Сценарий получения списка заказов пользователя."""

    uow: UnitOfWorkProtocol

    async def __call__(self, user_id: int) -> list[OrderDTO]:
        """Возвращает заказы пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            list[OrderDTO]: Список заказов пользователя.
        """
        async with self.uow:
            orders = await self.uow.order_repo.list_by_user(user_id)
        return [order_to_dto(order) for order in orders]
