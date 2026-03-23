"""Тесты для refresh токенов."""

import pytest


@pytest.mark.anyio
async def test_refresh_success(auth_client):
    """Тест успешного refresh токенов."""
    import asyncio

    # Получаем старые токены из cookies
    old_access = auth_client.cookies.get("access_token")
    old_refresh = auth_client.cookies.get("refresh_token")
    assert old_access is not None
    assert old_refresh is not None

    # Небольшая задержка чтобы exp отличался
    await asyncio.sleep(1)

    # Refresh
    response = await auth_client.post("/v1/auth/refresh")

    assert response.status_code == 200
    assert old_access != auth_client.cookies.get("access_token")
    assert old_refresh != auth_client.cookies.get("refresh_token")

    # Проверяем что cookies обновились
    assert auth_client.cookies.get("access_token") is not None
    assert auth_client.cookies.get("refresh_token") is not None


@pytest.mark.anyio
async def test_refresh_blacklisted_token(db_connect):
    """Тест refresh с заблокированным токеном."""
    # Регистрация и login
    await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        },
    )

    await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    # Сохраняем refresh токен
    refresh_token = db_connect.cookies.get("refresh_token")
    assert refresh_token is not None

    # Logout (блокирует токены)
    await db_connect.post("/v1/auth/logout")

    # Пробуем сделать refresh с заблокированным токеном (вручную)
    response = await db_connect.post(
        "/v1/auth/refresh",
        cookies={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Token has been revoked"
