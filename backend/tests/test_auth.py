import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app


@pytest_asyncio.fixture
async def client():
    """Фикстура для асинхронного клиента"""
    # Правильный способ создания AsyncClient для ASGI приложения
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Тест регистрации нового пользователя"""
    response = await client.post(
        "/register",
        json={
            "name": "test",
            "email": "testmail@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Тест входа пользователя"""
    # Сначала регистрируем
    await client.post(
        "/register",
        json={
            "name": "test",
            "email": "testmail@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )
