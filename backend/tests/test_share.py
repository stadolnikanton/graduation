"""
Простые тесты share функционала
"""
import pytest


@pytest.mark.asyncio
async def test_share_endpoint_exists():
    """Проверяем, что эндпоинты share доступны"""
    from httpx import AsyncClient
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Share endpoint
        response = await client.get("/share/invalid_token")
        
        # Может быть 404 (токен не найден) или 410 (истек)
        # Главное - не 500 (серверная ошибка)
        print(f"Share endpoint: {response.status_code}")
        assert response.status_code != 500
        
        # Проверяем, что есть описание ошибки
        if response.status_code >= 400:
            assert len(response.text) > 0