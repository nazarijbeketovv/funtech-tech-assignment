"""Контракт (Protocol) Unit of Work.

Unit of Work объединяет репозитории и управляет транзакционностью работы с БД.
Используется прикладными сценариями для выполнения набора операций с гарантией
commit/rollback.
"""

from typing import Protocol, Self
from types import TracebackType
from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    UserRepositoryProtocol,
)


class UnitOfWorkProtocol(Protocol):
    """Протокол unit-of-work с набором репозиториев и транзакциями."""

    user_repo: UserRepositoryProtocol
    order_repo: OrderRepositoryProtocol
    outbox_repo: OutboxRepositoryProtocol

    async def __aenter__(self) -> Self:
        """Входит в контекст unit-of-work.

        Returns:
            Self: Экземпляр unit-of-work.
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Выходит из контекста unit-of-work.

        При исключении обычно выполняется rollback.

        Args:
            exc_type: Тип исключения, если было.
            exc_val: Экземпляр исключения, если был.
            exc_tb: Traceback исключения, если был.

        Returns:
            bool | None: Семантика как у контекстного менеджера.
        """
        ...

    async def commit(self) -> None:
        """Фиксирует транзакцию."""
        ...

    async def rollback(self) -> None:
        """Откатывает транзакцию."""
        ...
