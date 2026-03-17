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
