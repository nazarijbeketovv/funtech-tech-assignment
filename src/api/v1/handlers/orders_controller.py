"""HTTP-обработчики для работы с заказами.

Модуль содержит эндпоинты для:
- создания заказа (только авторизованный пользователь);
- получения заказа по ID (с кешированием на уровне use-case);
- обновления статуса заказа;
- получения списка заказов пользователя.
"""

from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from application.dtos.order import CreateOrderDTO, UpdateOrderStatusDTO
from application.interfaces.repositories import UserRepositoryProtocol
from application.services.security import TokenService
from application.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListUserOrdersUseCase,
    UpdateOrderStatusUseCase,
)
from application.exceptions import InvalidCredentialsError
from domain.entities.user import User
from api.v1.mappers import OrderPresentationMapper
from api.v1.schemas import (
    OrderCreateSchema,
    OrderResponseSchema,
    OrderUpdateSchema,
)

router = APIRouter(tags=["Заказы"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/")


@inject
async def get_current_user(
    token_service: FromDishka[TokenService],
    users_repo: FromDishka[UserRepositoryProtocol],
    token: str = Depends(oauth2_scheme),
) -> User:
    """Возвращает текущего пользователя по JWT-токену.

    Достаёт токен из заголовка `Authorization: Bearer ...`, декодирует его и
    загружает пользователя из репозитория.

    Args:
        token_service: Сервис для работы с JWT-токенами.
        users_repo: Репозиторий пользователей.
        token: JWT-токен доступа.

    Returns:
        User: Доменная сущность пользователя.

    Raises:
        HTTPException: Если токен невалиден, пользователь не найден или запись
            пользователя некорректна.
    """
    try:
        data = token_service.decode_token(token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные учётные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await users_repo.get_by_id(data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректная запись пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def _require_user_id(user: User) -> int:
    """Извлекает идентификатор пользователя или выбрасывает HTTP 401.

    Args:
        user: Доменная сущность пользователя.

    Returns:
        int: Идентификатор пользователя.

    Raises:
        HTTPException: Если `user.id` отсутствует (некорректная запись).
    """
    user_id = user.id
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректная запись пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


@router.post(
    "/orders/",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_order(
    payload: OrderCreateSchema,
    mapper: FromDishka[OrderPresentationMapper],
    use_case: FromDishka[CreateOrderUseCase],
    current_user: User = Depends(get_current_user),
) -> OrderResponseSchema:
    """Создаёт заказ от имени текущего пользователя.

    Args:
        payload: Тело запроса на создание заказа.
        mapper: Маппер для преобразования DTO в схему ответа.
        use_case: Сценарий создания заказа.
        current_user: Авторизованный пользователь.

    Returns:
        OrderResponseSchema: Созданный заказ.
    """
    user_id = _require_user_id(current_user)
    dto = await use_case(
        CreateOrderDTO(
            user_id=user_id,
            items=payload.items,
            total_price=payload.total_price,
        )
    )
    return mapper.to_response(dto)


@router.get("/orders/{order_id}/", response_model=OrderResponseSchema)
@inject
async def get_order(
    order_id: UUID,
    mapper: FromDishka[OrderPresentationMapper],
    use_case: FromDishka[GetOrderUseCase],
    current_user: User = Depends(get_current_user),
) -> OrderResponseSchema:
    """Возвращает заказ по идентификатору.

    Args:
        order_id: Идентификатор заказа.
        mapper: Маппер для преобразования DTO в схему ответа.
        use_case: Сценарий получения заказа (с кешированием на его уровне).
        current_user: Авторизованный пользователь.

    Returns:
        OrderResponseSchema: Найденный заказ.
    """
    user_id = _require_user_id(current_user)
    dto = await use_case(order_id, user_id=user_id)
    return mapper.to_response(dto)


@router.patch("/orders/{order_id}/", response_model=OrderResponseSchema)
@inject
async def update_order_status(
    order_id: UUID,
    payload: OrderUpdateSchema,
    mapper: FromDishka[OrderPresentationMapper],
    use_case: FromDishka[UpdateOrderStatusUseCase],
    current_user: User = Depends(get_current_user),
) -> OrderResponseSchema:
    """Обновляет статус заказа.

    Args:
        order_id: Идентификатор заказа.
        payload: Тело запроса на обновление статуса.
        mapper: Маппер для преобразования DTO в схему ответа.
        use_case: Сценарий обновления статуса заказа.
        current_user: Авторизованный пользователь.

    Returns:
        OrderResponseSchema: Заказ с обновлённым статусом.
    """
    user_id = _require_user_id(current_user)
    dto = await use_case(
        UpdateOrderStatusDTO(
            order_id=order_id, status=payload.status, user_id=user_id
        )
    )
    return mapper.to_response(dto)


@router.get("/orders/user/{user_id}/", response_model=list[OrderResponseSchema])
@inject
async def list_user_orders(
    user_id: int,
    mapper: FromDishka[OrderPresentationMapper],
    use_case: FromDishka[ListUserOrdersUseCase],
    current_user: User = Depends(get_current_user),
) -> list[OrderResponseSchema]:
    """Возвращает список заказов конкретного пользователя.

    Доступ разрешён только владельцу (текущему пользователю).

    Args:
        user_id: Идентификатор пользователя, заказы которого запрашиваются.
        mapper: Маппер для преобразования DTO в схемы ответа.
        use_case: Сценарий получения списка заказов пользователя.
        current_user: Авторизованный пользователь.

    Returns:
        list[OrderResponseSchema]: Список заказов пользователя.

    Raises:
        HTTPException: Если запрошен список заказов другого пользователя.
    """
    current_user_id = _require_user_id(current_user)
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Запрещено запрашивать заказы другого пользователя",
        )
    dtos = await use_case(user_id)
    return mapper.to_list(dtos)
