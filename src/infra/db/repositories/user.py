"""Репозиторий пользователей на SQLAlchemy."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.repositories import UserRepositoryProtocol
from domain.entities.user import User
from infra.db.models import UserModel


@dataclass(slots=True, kw_only=True)
class UserRepositorySQLAlchemy(UserRepositoryProtocol):
    """SQLAlchemy-репозиторий пользователей."""

    session: AsyncSession

    async def get_by_email(self, email: str) -> User | None:
        """Возвращает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            User | None: Пользователь или `None`, если не найден.
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def get_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            User | None: Пользователь или `None`, если не найден.
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model)

    async def create(self, user: User) -> User:
        """Создаёт пользователя.

        Args:
            user: Доменная сущность пользователя.

        Returns:
            User: Созданный пользователь.
        """
        model = UserModel(email=user.email, hashed_password=user.hashed_password)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity_required(model)

    def _to_entity(self, model: UserModel | None) -> User | None:
        """Преобразует ORM-модель в доменную сущность (или `None`)."""
        if model is None:
            return None
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )

    def _to_entity_required(self, model: UserModel) -> User:
        """Преобразует ORM-модель в доменную сущность (обязательная)."""
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )
