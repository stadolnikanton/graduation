import asyncio

from .client import RedisClient


async def test():
    redis = RedisClient("localhost", 6379, 0)
    await redis.connect()
    print("connected")
    await redis.close()


asyncio.run(test())
