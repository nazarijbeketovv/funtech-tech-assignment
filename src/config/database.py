from typing import cast

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_server: str = Field(..., alias="POSTGRES_SERVER")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(..., alias="POSTGRES_DB")

    @computed_field
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @computed_field
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        return cast("PostgresDsn", self.database_url)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
