class DomainError(Exception):
    status_code = 500
    default_message = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message


class UserNotFoundError(DomainError):
    status_code = 404
    default_message = "User not found"


class EmailAlreadyExistsError(DomainError):
    status_code = 400
    default_message = "Email already registered"


class UsernameAlreadyExistError(DomainError):
    status_code = 400
    default_message = "Username already registered"


class InvalidCredentialError(DomainError):
    status_code = 401
    default_message = "Invalid credentials"


class TokenBlacklistedError(DomainError):
    status_code = 401
    default_message = "Token has been revoked"


class InvalidTokenError(DomainError):
    status_code = 401
    default_message = "Invalid token"


class FileSizeExceededError(DomainError):
    status_code = 413
    default_message = "File size exceeds maximum allowed"

class FileAlreadyExistsError(DomainError):
    status_code = 409
    default_message = ""
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"File with name '{self.filename}' already exists")


class FileUploadError(DomainError):
    status_code = 500
    default_message = "Failed to upload file to storage"