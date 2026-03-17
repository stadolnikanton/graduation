# TODO(REFACTOR-AUTH): Реализовать refresh() — обновление токенов
# TODO(REFACTOR-LOGGING): Добавить логирование

import time

from fastapi import Request

from domain.errors import (EmailAlreadyExistsError, InvalidCredentialError,
                           TokenBlacklistedError, UsernameAlreadyExistError)
from domain.user.entities import User
from infrastructure.jwt.service import JWTService
from infrastructure.redis.client import RedisClient
from infrastructure.repositories.user import UserRepository
from infrastructure.security.password import hash_password, verify_password
from schemas.requests.authentication import LoginRequest, RegisterRequest


class AuthenticationService:
    def __init__(
        self,
        user_repo: UserRepository,
        jwt_service: JWTService,
        redis_client: RedisClient,
    ) -> None:
        self.redis_client = redis_client
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

    async def logout(
        self,
        request: Request,
    ):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if access_token:
            await self.__block_token(access_token)
        if refresh_token:
            await self.__block_token(refresh_token)

    async def refresh(self, request: Request):
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            is_blocked_token = await self.redis_client.is_blacklisted(refresh_token)
            if is_blocked_token:
                raise TokenBlacklistedError()

            payload = self.jwt_service.verify_token(refresh_token)

            if payload.get("type") != "refresh":
                raise TokenBlacklistedError()
            user_id = int(payload.get("sub"))
            result = await self.user_repo.get_by_id(user_id)

            if result:
                await self.__block_token(refresh_token)
                data = {"sub": str(result.id)}
                access_token = self.jwt_service.create_access_token(data)
                refresh_token = self.jwt_service.create_refresh_token(data)

            return {
                "user": result,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

    async def me(self, user):
        return await self.user_repo.get_by_id(user)

    async def __block_token(self, token):
        payload = self.jwt_service.verify_token(token)
        if payload:
            ttl = payload.get("exp") - int(time.time())
            if ttl > 0:
                await self.redis_client.blacklist_token(token, ttl)
