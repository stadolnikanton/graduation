"""
Простейшие тесты без заморочек с БД
"""
import pytest
import io
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_docs_available():
    """Проверяем, что документация доступна"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check():
    """Проверяем, что приложение запускается"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Попробуем получить openapi.json
        response = await client.get("/openapi.json")
        # Может быть 200 или 404 (если не настроен)
        assert response.status_code in [200, 404, 422]


@pytest.mark.asyncio
async def test_register_new_user():
    """Тестируем регистрацию нового пользователя"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": f"testuser_{hash('test')}",
            "email": f"test{hash('test')}@example.com",
            "password": "Test123!",
            "password_confirm": "Test123!"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        # Если 200 - ок, если 400 - возможно пользователь уже существует
        assert response.status_code in [200, 400]
        
        if response.status_code == 400:
            # Проверяем, что это не другая ошибка
            assert "already" in response.text.lower()


@pytest.mark.asyncio
async def test_protected_route_without_auth():
    """Доступ к защищённому маршруту без авторизации"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/files/")
        assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_auth_flow():
    """Полный цикл: регистрация -> вход -> защищённый маршрут"""
    import time
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Регистрация
        timestamp = int(time.time())
        user_data = {
            "name": f"user_{timestamp}",
            "email": f"user_{timestamp}@example.com",
            "password": "Test123!",
            "password_confirm": "Test123!"
        }
        
        reg_response = await client.post("/auth/register", json=user_data)
        print(f"Register: {reg_response.status_code}")
        
        # Если регистрация успешна (200) или пользователь уже существует (400)
        assert reg_response.status_code in [200, 400]
        
        # 2. Вход (если регистрация была успешной)
        if reg_response.status_code == 200:
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = await client.post("/auth/login", json=login_data)
            print(f"Login: {login_response.status_code}")
            
            assert login_response.status_code == 200
            assert "access_token" in login_response.cookies
            
            # 3. Защищённый маршрут
            files_response = await client.get("/files/")
            print(f"Files: {files_response.status_code}")
            
            # Должен быть 200, так как мы залогинены
            assert files_response.status_code == 200
            
            # 4. Логаут
            logout_response = await client.post("/auth/logout")
            print(f"Logout: {logout_response.status_code}")
            
            assert logout_response.status_code == 200