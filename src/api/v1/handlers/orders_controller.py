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

router = APIRouter(tags=["Orders"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/")


@inject
async def get_current_user(
    token_service: FromDishka[TokenService],
    users_repo: FromDishka[UserRepositoryProtocol],
    token: str = Depends(oauth2_scheme),
) -> User:
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
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await users_repo.get_by_id(data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User record is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


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
    dto = await use_case(
        CreateOrderDTO(
            user_id=current_user.id,
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
    dto = await use_case(order_id, user_id=current_user.id)
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
    dto = await use_case(
        UpdateOrderStatusDTO(
            order_id=order_id, status=payload.status, user_id=current_user.id
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
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access other user's orders",
        )
    dtos = await use_case(user_id)
    return mapper.to_list(dtos)
