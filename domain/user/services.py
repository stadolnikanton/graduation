from domain.user.entities import User
from schemas.requests.authentication import LoginRequest, RegisterRequest
from schemas.requests.token import Token


class AuthenticationService:
    def __init__(self) -> None:
        pass

    async def register(self, data: RegisterRequest) -> User:
        pass

    def login(self, data: LoginRequest) -> User:
        pass

    def logout(self):
        pass

    def refresh(self):
        pass
