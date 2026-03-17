# TODO(REFACTOR-ERRORS): Использовать эти классы в domain/user/services.py
# TODO(REFACTOR-ERRORS): Добавить больше ошибок (WeakPasswordError, TokenExpiredError)
# TODO(REFACTOR-ERRORS): Добавить HTTP статус коды к ошибкам
# TODO(REFACTOR-ERRORS): Создать базовый класс для HTTP ошибок


class DomainError(ValueError):
    pass


class UserNotFoundError(DomainError):
    pass


class EmailAlreadyExistsError(DomainError):
    pass


class UsernameAlreadyExistError(DomainError):
    pass


class InvalidCredentialError(DomainError):
    pass


class TokenBlacklistedError(DomainError):
    pass


class InvalidTokenError(DomainError):
    pass
