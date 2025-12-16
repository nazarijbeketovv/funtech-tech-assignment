from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from application.exceptions import (
    ApplicationError,
    InvalidCredentialsError,
    OrderNotFoundError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from domain.exceptions import DomainValidationError


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(
        _: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        _: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_handler(
        _: Request, exc: OrderNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        _: Request, exc: UnauthorizedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(
        _: Request, exc: DomainValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        _: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
