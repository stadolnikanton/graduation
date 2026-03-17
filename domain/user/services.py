# TODO(REFACTOR-AUTH): Реализовать logout() — blacklist токенов через Redis
# TODO(REFACTOR-AUTH): Реализовать refresh() — обновление токенов
# TODO(REFACTOR-LOGGING): Добавить логирование

from domain.errors import (EmailAlreadyExistsError, InvalidCredentialError,
                           UsernameAlreadyExistError)
from domain.user.entities import User
from infrastructure.jwt.service import JWTService
from infrastructure.repositories.user import UserRepository
from infrastructure.security.password import hash_password, verify_password
from schemas.requests.authentication import LoginRequest, RegisterRequest


class AuthenticationService:
    def __init__(self, user_repo: UserRepository, jwt_service: JWTService) -> None:
        self.user_repo = user_repo
        self.jwt_service = jwt_service

    async def register(
        self,
        data: RegisterRequest,
    ) -> dict:
        exists = await self.user_repo.get_by_email(data.email)
        if exists:
            raise EmailAlreadyExistsError()
        exists = await self.user_repo.get_by_username(data.username)
        if exists:
            raise UsernameAlreadyExistError()
        password_hash = hash_password(data.password)

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            password_hash=password_hash,
        )
        created_user = await self.user_repo.create(user)

        access_token = self.jwt_service.create_access_token(
            data={"sub": str(created_user.id)}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={"sub": str(created_user.id)}
        )

        return {
            "user": created_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def login(self, data: LoginRequest) -> dict:
        exists_user = await self.user_repo.username_or_email(data.username_or_email)
        if not exists_user or not verify_password(
            data.password, exists_user.password_hash
        ):
            raise InvalidCredentialError()
        access_token = self.jwt_service.create_access_token(
            data={"sub": str(exists_user.id)}
        )
        refresh_token = self.jwt_service.create_refresh_token(
            data={"sub": str(exists_user.id)}
        )

        return {
            "user": exists_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def logout(self):
        pass

    def refresh(self):
        pass
