from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_maker
from domain.errors import (InvalidTokenError, TokenBlacklistedError,
                           UserNotFoundError)
from domain.file.services import FileUploadService
from domain.user.services import AuthenticationService
from infrastructure.jwt.service import JWTService
from infrastructure.minio.client import MinioClient
from infrastructure.redis.client import RedisClient
from infrastructure.repositories.user import UserRepository
from infrastructure.security.cookies import (delete_auth_cookies,
                                             set_auth_cookies,
                                             set_auth_cookies_with_user_data)

from infrastructure.repositories.file import FileRepository


# Возвращает сессию базы данных
async def get_database():
    async with async_session_maker() as session:
        yield session


# Возвращает клиент minio
def get_minio_client():
    return MinioClient(
        settings.MINIO_ENDPOINT,
        settings.MINIO_PORT_API,
        settings.MINIO_ROOT_USER,
        settings.MINIO_ROOT_PASSWORD.get_secret_value(),
    )


# Возвращает клиент redis
def get_redis_client():
    return RedisClient(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)


async def get_jwt_service():
    return JWTService(settings.SECRET_KEY.get_secret_value(), settings.ALGORITHM)


async def get_user_repo(
    session: AsyncSession = Depends(get_database),
) -> UserRepository:
    return UserRepository(session)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    jwt_service: JWTService = Depends(get_jwt_service),
    redis_client: RedisClient = Depends(get_redis_client),
) -> AuthenticationService:
    return AuthenticationService(user_repo, jwt_service, redis_client)


async def get_file_repo(session: AsyncSession = Depends(get_database)) -> FileRepository:
    return FileRepository(session)


async def get_file_service(
        minio_client: MinioClient = Depends(get_minio_client),
        file_repo: FileRepository = Depends(get_file_repo),
) -> FileUploadService:
    return FileUploadService(minio_client, file_repo)


class AuthCookies:
    """Класс для удобного управления auth cookies через Depends"""

    def __init__(self, response: Response) -> None:
        self.response = response

    def set(
        self,
        access_token: str,
        refresh_token: str,
        secure: bool | None = None,
        path: str = "/",
    ) -> None:
        set_auth_cookies(self.response, access_token, refresh_token, secure, path)

    def delete(self, path: str = "/") -> None:
        delete_auth_cookies(self.response, path)

    def set_with_user_data(
        self,
        access_token: str,
        refresh_token: str,
        user_data: Dict[str, Any],
        secure: Optional[bool] = None,
        path: str = "/",
    ) -> None:
        set_auth_cookies_with_user_data(
            self.response, access_token, refresh_token, user_data, secure, path
        )

    def set_custom(
        self,
        key: str,
        value: str,
        max_age: int = None,
        httponly: bool = True,
        secure: bool = None,
        samesite: str = "strict",
        path: str = "/",
    ) -> None:
        if secure is None:
            secure = False

        self.response.set_cookie(
            key=key,
            value=value,
            httponly=httponly,
            max_age=max_age,
            secure=secure,
            samesite=samesite,
            path=path,
        )


def get_auth_cookies(response: Response) -> AuthCookies:
    return AuthCookies(response)


async def get_current_user(
    request: Request,
    jwt_service: JWTService = Depends(get_jwt_service),
    user_repo: UserRepository = Depends(get_user_repo),
    redis_client: RedisClient = Depends(get_redis_client),
) -> Dict:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    is_blacklist = await redis_client.is_blacklisted(access_token)

    if is_blacklist:
        raise TokenBlacklistedError()

    payload = jwt_service.verify_token(access_token)

    if not payload:
        raise InvalidTokenError()

    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise InvalidTokenError()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError()

    user = await user_repo.get_by_id(int(user_id))

    if not user:
        raise UserNotFoundError()

    return user
