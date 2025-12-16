import logging
from dataclasses import dataclass
from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession
from types import TracebackType
from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    UserRepositoryProtocol,
)
from application.interfaces.uow import UnitOfWorkProtocol

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class UnitOfWorkSQLAlchemy(UnitOfWorkProtocol):
    session: AsyncSession
    user_repo: UserRepositoryProtocol
    order_repo: OrderRepositoryProtocol
    outbox_repo: OutboxRepositoryProtocol

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if exc_type:
            await self.rollback()
        return None

    async def commit(self) -> None:
        logger.debug("Committing transaction")
        await self.session.commit()

    async def rollback(self) -> None:
        logger.debug("Rolling back transaction")
        await self.session.rollback()
