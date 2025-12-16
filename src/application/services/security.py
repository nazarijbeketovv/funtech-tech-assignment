from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from application.dtos.auth import TokenDTO, TokenDataDTO
from application.exceptions import InvalidCredentialsError


class PasswordHasher:
    def __init__(self) -> None:
        self._context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self._context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._context.verify(password, hashed_password)


class TokenService:
    def __init__(
        self, *, secret_key: str, algorithm: str, expires_delta: timedelta
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_delta = expires_delta

    def create_access_token(self, *, user_id: int, email: str) -> TokenDTO:
        expire = datetime.now(UTC) + self.expires_delta
        to_encode = {"sub": str(user_id), "email": email, "exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return TokenDTO(access_token=encoded_jwt)

    def decode_token(self, token: str) -> TokenDataDTO:
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            user_id = payload.get("sub")
            email = payload.get("email")
            if user_id is None:
                raise InvalidCredentialsError("Token missing subject")
            return TokenDataDTO(user_id=int(user_id), email=email)
        except JWTError as exc:
            raise InvalidCredentialsError(
                "Could not validate credentials"
            ) from exc
