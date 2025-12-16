from pydantic import Field
from pydantic_settings import BaseSettings


class CORSSettings(BaseSettings):
    cors_origins: list[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"], alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(
        ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        alias="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: list[str] = Field(["*"], alias="CORS_ALLOW_HEADERS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
