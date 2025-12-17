"""Доменная сущность пользователя."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from domain.exceptions import DomainValidationError


@dataclass(slots=True, frozen=True, kw_only=True)
class User:
    """Пользователь как доменная сущность.

    Инварианты:
    - `email` должен выглядеть как корректный адрес (упрощённая проверка)
    - `hashed_password` не пустой

    Attributes:
        email: Email пользователя.
        hashed_password: Хеш пароля.
        id: Идентификатор пользователя (заполняется при сохранении).
        created_at: Время создания пользователя (UTC).
    """

    email: str
    hashed_password: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Проверяет доменные инварианты после создания объекта.

        Raises:
            DomainValidationError: Если email/пароль не удовлетворяют правилам.
        """
        if "@" not in self.email or len(self.email) < 5:
            raise DomainValidationError("Email невалидный.")
        if not self.hashed_password:
            raise DomainValidationError("Отсутствует пароль.")
