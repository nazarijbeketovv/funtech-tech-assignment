"""Реализация Unit of Work на базе SQLAlchemy."""

from dataclasses import dataclass
from types import TracebackType
from typing import Self

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    UserRepositoryProtocol,
)
from application.interfaces.uow import UnitOfWorkProtocol


@dataclass(slots=True, kw_only=True)
class UnitOfWorkSQLAlchemy(UnitOfWorkProtocol):
    """Unit of Work для работы с БД через `AsyncSession`."""

    session: AsyncSession
    user_repo: UserRepositoryProtocol
    order_repo: OrderRepositoryProtocol
    outbox_repo: OutboxRepositoryProtocol

    async def __aenter__(self) -> Self:
        """Входит в контекст unit-of-work."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Выходит из контекста unit-of-work.

        При наличии исключения выполняется rollback.
        """
        if exc_type:
            await self.rollback()
        return None

    async def commit(self) -> None:
        """Фиксирует транзакцию."""
        logger.debug("Фиксация транзакции")
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатывает транзакцию."""
        logger.debug("Откат транзакции")
        await self.session.rollback()
