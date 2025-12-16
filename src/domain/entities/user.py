from dataclasses import dataclass, field
from datetime import UTC, datetime

from domain.exceptions import DomainValidationError


@dataclass(slots=True, frozen=True, kw_only=True)
class User:
    email: str
    hashed_password: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if "@" not in self.email or len(self.email) < 5:
            raise DomainValidationError("Email невалидный.")
        if not self.hashed_password:
            raise DomainValidationError("Отсутствует пароль.")
