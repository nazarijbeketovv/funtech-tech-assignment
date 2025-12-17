"""DTO для аутентификации/авторизации."""

from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class TokenDTO:
    """DTO токена доступа.

    Attributes:
        access_token: Строковое представление JWT.
        token_type: Тип токена (по умолчанию `bearer`).
    """

    access_token: str
    token_type: str = "bearer"


@dataclass(slots=True, kw_only=True)
class TokenDataDTO:
    """Данные, извлечённые из токена.

    Attributes:
        user_id: Идентификатор пользователя (subject).
        email: Email пользователя, если присутствует в payload.
    """

    user_id: int | None = None
    email: str | None = None
