"""Pydantic-схемы для аутентификации и пользователей.

Схемы используются в HTTP-эндпоинтах регистрации/логина и в ответах API.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterSchema(BaseModel):
    """Схема запроса регистрации пользователя."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginSchema(BaseModel):
    """Схема запроса входа пользователя (email/пароль)."""

    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    """Схема ответа с токеном доступа."""

    access_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    """Схема ответа с данными пользователя."""

    id: int
    email: EmailStr
    created_at: str
