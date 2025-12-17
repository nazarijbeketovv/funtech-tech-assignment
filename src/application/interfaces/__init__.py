"""Публичные интерфейсы (контракты) прикладного слоя.

Модуль реэкспортирует Protocol-интерфейсы, используемые use-case'ами.
"""

from application.interfaces.cache import CacheProtocol
from application.interfaces.message_broker import MessageBrokerPublisherProtocol
from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    UserRepositoryProtocol,
)
from application.interfaces.uow import UnitOfWorkProtocol

__all__ = [
    "CacheProtocol",
    "MessageBrokerPublisherProtocol",
    "OrderRepositoryProtocol",
    "UnitOfWorkProtocol",
    "UserRepositoryProtocol",
]
