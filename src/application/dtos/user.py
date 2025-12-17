"""DTO для пользователей."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class UserDTO:
    """DTO пользователя, используемый в ответах/внутренних сценариях.

    Attributes:
        id: Идентификатор пользователя.
        email: Email пользователя.
        created_at: Дата и время создания пользователя.
    """

    id: int
    email: str
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class UserCreateDTO:
    """DTO для регистрации пользователя.

    Attributes:
        email: Email пользователя.
        password: Пароль в открытом виде (только на входе в use-case).
    """

    email: str
    password: str
