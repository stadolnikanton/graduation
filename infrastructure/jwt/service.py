# TODO(REFACTOR-JWT): Добавить async в методы (если нужен Redis)
# TODO(REFACTOR-JWT): Интегрировать Redis в verify_token() — проверка blacklist
# TODO(REFACTOR-JWT): Добавить методы для refresh токена (сохранение в Redis)
# TODO(REFACTOR-JWT): Добавить логирование
# TODO(REFACTOR-JWT): Обработать JWT ошибки (ExpiredSignatureError и т.д.)

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.config import settings


class JWTService:
    """Класс для работы с jwt"""

    def __init__(self, secret_key: str, algorithm: str, redis_client=None) -> None:
        self.secret_key: str = secret_key
        self.algorithm: str = algorithm
        self.redis = redis_client

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update(({"exp": expire, "type": "access"}))

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )

        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.PyJWTError:
            return None
