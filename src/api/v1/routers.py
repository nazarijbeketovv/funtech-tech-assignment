from fastapi import APIRouter

from api.v1.handlers import auth_router, orders_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(orders_router)
