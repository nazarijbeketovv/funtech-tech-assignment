"""HTTP-обработчики аутентификации и регистрации.

Содержит эндпоинты:
- `POST /register/` — регистрация пользователя;
- `POST /token/` — получение JWT-токена по OAuth2 Password Flow.
"""

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

router = APIRouter(tags=["Аутентификация"])


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
    """Регистрирует нового пользователя.

    Args:
        payload: Данные регистрации (email и пароль).
        use_case: Сценарий регистрации пользователя.

    Returns:
        UserResponseSchema: Данные созданного пользователя.
    """
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
    """Выдаёт JWT-токен доступа по логину и паролю.

    Args:
        use_case: Сценарий входа пользователя.
        form_data: OAuth2-форма (username/password).

    Returns:
        TokenSchema: Токен доступа и его тип.
    """
    token_dto = await use_case(
        email=form_data.username, password=form_data.password
    )
    return TokenSchema(
        access_token=token_dto.access_token, token_type=token_dto.token_type
    )
