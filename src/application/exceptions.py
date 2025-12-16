class ApplicationError(Exception): ...


class UserAlreadyExistsError(ApplicationError):
    pass


class InvalidCredentialsError(ApplicationError):
    pass


class OrderNotFoundError(ApplicationError):
    pass


class UnauthorizedError(ApplicationError):
    pass
