"""Сервисы безопасности: хеширование паролей и JWT-токены."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from application.dtos.auth import TokenDTO, TokenDataDTO
from application.exceptions import InvalidCredentialsError


class PasswordHasher:
    """Сервис хеширования и проверки паролей."""

    def __init__(self) -> None:
        """Создаёт хешер паролей с настроенным `CryptContext`."""
        self._context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Хеширует пароль.

        Args:
            password: Пароль в открытом виде.

        Returns:
            str: Хеш пароля.
        """
        return self._context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        """Проверяет пароль по сохранённому хешу.

        Args:
            password: Пароль в открытом виде.
            hashed_password: Сохранённый хеш.

        Returns:
            bool: `True`, если пароль верный, иначе `False`.
        """
        return self._context.verify(password, hashed_password)


class TokenService:
    """Сервис создания и проверки JWT-токенов."""

    def __init__(
        self, *, secret_key: str, algorithm: str, expires_delta: timedelta
    ) -> None:
        """Создаёт сервис JWT с заданными параметрами подписи.

        Args:
            secret_key: Секретный ключ подписи.
            algorithm: Алгоритм подписи JWT.
            expires_delta: Время жизни токена.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_delta = expires_delta

    def create_access_token(self, *, user_id: int, email: str) -> TokenDTO:
        """Создаёт токен доступа.

        Args:
            user_id: Идентификатор пользователя (subject).
            email: Email пользователя.

        Returns:
            TokenDTO: DTO с токеном доступа.
        """
        expire = datetime.now(UTC) + self.expires_delta
        to_encode = {"sub": str(user_id), "email": email, "exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return TokenDTO(access_token=encoded_jwt)

    def decode_token(self, token: str) -> TokenDataDTO:
        """Декодирует и валидирует JWT-токен.

        Args:
            token: JWT-токен доступа.

        Returns:
            TokenDataDTO: Данные, извлечённые из токена.

        Raises:
            InvalidCredentialsError: Если токен невалиден или не содержит `sub`.
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            user_id = payload.get("sub")
            email = payload.get("email")
            if user_id is None:
                raise InvalidCredentialsError(
                    "В токене отсутствует subject (sub)"
                )
            return TokenDataDTO(user_id=int(user_id), email=email)
        except JWTError as exc:
            raise InvalidCredentialsError(
                "Не удалось проверить учётные данные"
            ) from exc
