# TODO(REFACTOR-REDIS): Реализовать save_refresh_token()
# TODO(REFACTOR-REDIS): Реализовать delete_refresh_tokens()
# TODO(REFACTOR-REDIS): Добавить type hints
# TODO(REFACTOR-REDIS): Обработать ошибки подключения
# TODO(REFACTOR-REDIS): Добавить логирование

import redis.asyncio as aioredis


class RedisClient:
    """Класс для работы с redis"""

    def __init__(self, host: str, port: str, db: str = 0) -> None:
        self.connection = aioredis.Redis(host=host, port=port, db=db)

    async def connect(self):
        await self.connection.ping()

    async def close(self):
        await self.connection.close()

    async def blacklist_token(self, token, ttl):
        await self.connection.setex(f"blacklist:{token}", ttl, "1")

    async def is_blacklisted(self, token):
        return await self.connection.exists(f"blacklist:{token}") == 1
