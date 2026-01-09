import pytest

from httpx import ASGITransport, AsyncClient

from sqlalchemy import text
from sqlalchemy.ext.asyncio import close_all_sessions

from app.main import app
from app.db import async_session_maker, engine

@pytest.fixture(autouse=True)
async def clean_db():
    """
    Простая очистка с TRUNCATE CASCADE.
    """
    async with async_session_maker() as session:
        await session.execute(text("TRUNCATE TABLE files, users CASCADE"))
        await session.commit()
    yield

    await close_all_sessions() # Закрывает все соединения
    await engine.dispose()

@pytest.fixture
async def db_connect():
    """
    Создает клиент для группы тестов (модуля).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac