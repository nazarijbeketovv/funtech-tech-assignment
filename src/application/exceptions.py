"""Исключения прикладного (application) слоя.

Содержит ошибки, которые отражают бизнес-сценарии и используются для
преобразования в корректные HTTP-ответы на уровне API.
"""


class ApplicationError(Exception):
    """Базовая ошибка прикладного слоя."""


class UserAlreadyExistsError(ApplicationError):
    """Пользователь с указанным email уже существует."""


class InvalidCredentialsError(ApplicationError):
    """Неверные учётные данные или невалидный токен."""


class OrderNotFoundError(ApplicationError):
    """Заказ не найден (либо недоступен пользователю)."""


class UnauthorizedError(ApplicationError):
    """Пользователь не имеет прав на выполнение действия."""
