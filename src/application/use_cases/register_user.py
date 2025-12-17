"""Use-case регистрации пользователя."""

from dataclasses import dataclass

from application.dtos.user import UserCreateDTO, UserDTO
from application.exceptions import UserAlreadyExistsError
from application.mappers import user_to_dto
from application.services.security import PasswordHasher
from application.interfaces.uow import UnitOfWorkProtocol
from domain.entities.user import User


@dataclass(slots=True, kw_only=True)
class RegisterUserUseCase:
    """Сценарий регистрации пользователя."""

    uow: UnitOfWorkProtocol
    password_hasher: PasswordHasher

    async def __call__(self, payload: UserCreateDTO) -> UserDTO:
        """Регистрирует пользователя.

        Args:
            payload: DTO с email и паролем.

        Returns:
            UserDTO: Созданный пользователь.

        Raises:
            UserAlreadyExistsError: Если пользователь с таким email уже существует.
        """
        async with self.uow:
            existing = await self.uow.user_repo.get_by_email(payload.email)
            if existing:
                raise UserAlreadyExistsError("Пользователь уже зарегистрирован")

            hashed = self.password_hasher.hash(payload.password)
            user = User(email=payload.email, hashed_password=hashed)
            created = await self.uow.user_repo.create(user)
            await self.uow.commit()

        return user_to_dto(created)
