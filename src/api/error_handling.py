"""Регистрация обработчиков исключений для FastAPI.

Модуль описывает единообразное преобразование доменных/прикладных ошибок в
HTTP-ответы с корректными кодами статуса и телом `{"detail": "..."}`.
"""

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
    """Регистрирует обработчики исключений в приложении.

    Args:
        app: Экземпляр FastAPI, в который будут добавлены handlers.
    """

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(
        _: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        """Обработчик ошибки регистрации уже существующего пользователя.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение домена/приложения.

        Returns:
            JSONResponse: Ответ с HTTP 400 и текстом ошибки.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        _: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        """Обработчик ошибки неверных учётных данных.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение домена/приложения.

        Returns:
            JSONResponse: Ответ с HTTP 401 и заголовком `WWW-Authenticate`.
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_handler(
        _: Request, exc: OrderNotFoundError
    ) -> JSONResponse:
        """Обработчик ошибки отсутствующего заказа.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение домена/приложения.

        Returns:
            JSONResponse: Ответ с HTTP 404 и текстом ошибки.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        _: Request, exc: UnauthorizedError
    ) -> JSONResponse:
        """Обработчик ошибки отсутствия прав на действие.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение домена/приложения.

        Returns:
            JSONResponse: Ответ с HTTP 403 и текстом ошибки.
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(
        _: Request, exc: DomainValidationError
    ) -> JSONResponse:
        """Обработчик ошибок валидации доменной модели.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение домена.

        Returns:
            JSONResponse: Ответ с HTTP 400 и текстом ошибки.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        _: Request, exc: ApplicationError
    ) -> JSONResponse:
        """Обработчик непредвиденных ошибок приложения.

        Args:
            _: HTTP-запрос (не используется).
            exc: Исключение приложения.

        Returns:
            JSONResponse: Ответ с HTTP 500 и текстом ошибки.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
