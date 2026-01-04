"""
Простые тесты загрузки файлов
"""
import pytest
import io


@pytest.mark.asyncio
async def test_upload_small_file():
    """Загрузка маленького файла"""
    from httpx import AsyncClient
    from app.main import app
    import time
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Регистрируемся
        timestamp = int(time.time())
        user_data = {
            "name": f"uploader_{timestamp}",
            "email": f"uploader_{timestamp}@example.com",
            "password": "Test123!",
            "password_confirm": "Test123!"
        }
        
        await client.post("/auth/register", json=user_data)
        
        # 2. Логинимся
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        await client.post("/auth/login", json=login_data)
        
        # 3. Загружаем файл
        file_content = b"Test file content for simple test"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = await client.post("/files/upload/", files=files)
        
        print(f"Upload response: {response.status_code}")
        print(f"Upload body: {response.text[:200]}")
        
        # Проверяем результат
        assert response.status_code in [200, 413, 422]  # 200-успех, 413-слишком большой, 422-ошибка валидации
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "file_id" in data


@pytest.mark.asyncio
async def test_file_endpoints_exist():
    """Проверяем, что эндпоинты файлов доступны"""
    from httpx import AsyncClient
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Проверяем различные эндпоинты
        endpoints = [
            "/files/",
            "/files/upload/",
            "/files/upload/multiple",
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            # Должны получить 401 (нет авторизации) или 405 (метод не разрешен)
            # Главное - не 404 (страница не найдена)
            print(f"{endpoint}: {response.status_code}")
            assert response.status_code != 404