from pydantic import BaseModel, EmailStr, Field


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    created_at: str
