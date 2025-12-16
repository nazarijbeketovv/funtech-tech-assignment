from dataclasses import dataclass

from application.dtos.auth import TokenDTO
from application.exceptions import InvalidCredentialsError
from application.services.security import PasswordHasher, TokenService
from application.interfaces.repositories import UserRepositoryProtocol


@dataclass(slots=True, kw_only=True)
class LoginUserUseCase:
    users: UserRepositoryProtocol
    password_hasher: PasswordHasher
    token_service: TokenService

    async def __call__(self, *, email: str, password: str) -> TokenDTO:
        user = await self.users.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError("Incorrect email or password")

        if not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password")

        if user.id is None:
            raise InvalidCredentialsError("User record is invalid")

        return self.token_service.create_access_token(
            user_id=user.id, email=user.email
        )
