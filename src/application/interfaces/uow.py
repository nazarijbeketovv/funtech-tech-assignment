from typing import Protocol, Self
from types import TracebackType
from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    UserRepositoryProtocol,
)


class UnitOfWorkProtocol(Protocol):
    user_repo: UserRepositoryProtocol
    order_repo: OrderRepositoryProtocol
    outbox_repo: OutboxRepositoryProtocol

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
