from datetime import timedelta

from pydantic import Field
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
