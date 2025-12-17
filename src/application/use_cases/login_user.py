"""Use-case входа пользователя (выдача JWT)."""

from dataclasses import dataclass

from application.dtos.auth import TokenDTO
from application.exceptions import InvalidCredentialsError
from application.services.security import PasswordHasher, TokenService
from application.interfaces.repositories import UserRepositoryProtocol


@dataclass(slots=True, kw_only=True)
class LoginUserUseCase:
    """Сценарий входа пользователя и выдачи токена доступа."""

    users: UserRepositoryProtocol
    password_hasher: PasswordHasher
    token_service: TokenService

    async def __call__(self, *, email: str, password: str) -> TokenDTO:
        """Проверяет учётные данные и возвращает JWT-токен.

        Args:
            email: Email пользователя.
            password: Пароль пользователя.

        Returns:
            TokenDTO: DTO токена доступа.

        Raises:
            InvalidCredentialsError: Если email/пароль неверны или пользователь
                находится в некорректном состоянии.
        """
        user = await self.users.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError("Неверный email или пароль")

        if not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidCredentialsError("Неверный email или пароль")

        if user.id is None:
            raise InvalidCredentialsError("Некорректная запись пользователя")

        return self.token_service.create_access_token(
            user_id=user.id, email=user.email
        )
