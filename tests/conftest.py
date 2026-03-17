import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import close_all_sessions

from app.database import async_session_maker, engine
from app.main import app


@pytest.fixture(autouse=True)
async def clean_db():
    """
    Очистка БД перед каждым тестом.
    """
    async with async_session_maker() as session:
        await session.execute(text("TRUNCATE TABLE files, users CASCADE"))
        await session.commit()
    yield

    await close_all_sessions()
    await engine.dispose()


@pytest.fixture
async def db_connect():
    """
    Базовый HTTP клиент для тестов.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def registered_user(db_connect):
    """
    Фикстура: зарегистрированный пользователь (без login).
    """
    user_data = {
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "TestPassword123",
        "password_confirm": "TestPassword123",
    }
    response = await db_connect.post("/v1/auth/register", json=user_data)
    assert response.status_code == 200
    return {
        "user_data": user_data,
        "tokens": response.json(),
    }


@pytest.fixture
async def auth_client(db_connect):
    """
    Фикстура: авторизованный клиент (register + login).
    """
    # Регистрация
    user_data = {
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "TestPassword123",
        "password_confirm": "TestPassword123",
    }
    response = await db_connect.post("/v1/auth/register", json=user_data)
    assert response.status_code == 200

    # Login
    response = await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    assert db_connect.cookies.get("access_token") is not None
    assert db_connect.cookies.get("refresh_token") is not None

    return db_connect


@pytest.fixture
async def auth_tokens(auth_client):
    """
    Фикстура: возвращает токены авторизованного клиента.
    """
    return {
        "access_token": auth_client.cookies.get("access_token"),
        "refresh_token": auth_client.cookies.get("refresh_token"),
    }
