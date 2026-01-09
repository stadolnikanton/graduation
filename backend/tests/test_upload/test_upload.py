import pytest


@pytest.mark.anyio
async def test_get_user_files_unauthorized(db_connect):
    """Тест получения файлов без авторизации"""
    response = await db_connect.get("/files/")
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_upload_file_simple(db_connect):
    """Простой тест загрузки файла"""
    # Создаем тестовый файл
    test_content = b"Test file content for upload"
    
    # Пробуем загрузить файл без авторизации
    response = await db_connect.post(
        "/files/upload",
        files={"file": ("test.txt", test_content, "text/plain")}
    )
    
    # Должна быть ошибка авторизации
    assert response.status_code == 401


@pytest.mark.anyio
async def test_download_file_unauthorized(db_connect):
    """Тест скачивания файла без авторизации"""
    response = await db_connect.get("/files/1/download")
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_delete_file_unauthorized(db_connect):
    """Тест удаления файла без авторизации"""
    response = await db_connect.delete("/files/1")
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_share_file_unauthorized(db_connect):
    """Тест предоставления доступа к файлу без авторизации"""
    response = await db_connect.post(
        "/files/1/share",
        json={"user_id": 1, "access_level": "read"}
    )
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_shared_users_unauthorized(db_connect):
    """Тест получения списка пользователей с доступом без авторизации"""
    response = await db_connect.get("/files/1/shared-users")
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_remove_share_unauthorized(db_connect):
    """Тест удаления доступа к файлу без авторизации"""
    response = await db_connect.delete("/files/1/share/2")
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_upload_multiple_files_unauthorized(db_connect):
    """Тест загрузки нескольких файлов без авторизации"""
    test_content = b"Test content"
    
    response = await db_connect.post(
        "/files/upload/multiple",
        files=[
            ("files", ("file1.txt", test_content, "text/plain")),
            ("files", ("file2.txt", test_content, "text/plain"))
        ]
    )
    
    assert response.status_code == 401