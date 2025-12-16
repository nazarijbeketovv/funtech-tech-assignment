from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from application.dtos.user import UserCreateDTO
from application.use_cases import LoginUserUseCase, RegisterUserUseCase
from api.v1.schemas import (
    RegisterSchema,
    TokenSchema,
    UserResponseSchema,
)

router = APIRouter(tags=["Auth"])


@router.post(
    "/register/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register_user(
    payload: RegisterSchema,
    use_case: FromDishka[RegisterUserUseCase],
) -> UserResponseSchema:
    user_dto = await use_case(
        UserCreateDTO(email=payload.email, password=payload.password)
    )
    return UserResponseSchema(
        id=user_dto.id,
        email=user_dto.email,
        created_at=user_dto.created_at.isoformat(),
    )


@router.post("/token/", response_model=TokenSchema)
@inject
async def login_for_access_token(
    use_case: FromDishka[LoginUserUseCase],
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenSchema:
    token_dto = await use_case(
        email=form_data.username, password=form_data.password
    )
    return TokenSchema(
        access_token=token_dto.access_token, token_type=token_dto.token_type
    )
