"""Тесты для получения текущего пользователя (/me)."""

import pytest


@pytest.mark.anyio
async def test_me_success(auth_client):
    """Тест успешного получения текущего пользователя."""
    response = await auth_client.get("/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"
    assert "first_name" in data
    assert "last_name" in data
    # Password hash не должен возвращаться
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_me_no_token(db_connect):
    """Тест получения пользователя без токена."""
    response = await db_connect.get("/v1/auth/me")

    assert response.status_code == 401
    data = response.json()
    # HTTPException возвращает detail
    assert "detail" in data


@pytest.mark.anyio
async def test_me_invalid_token(db_connect):
    """Тест получения пользователя с невалидным токеном."""
    response = await db_connect.get(
        "/v1/auth/me",
        cookies={"access_token": "invalid_token_here"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Invalid token"


@pytest.mark.anyio
async def test_me_blacklisted_token(auth_client):
    """Тест получения пользователя с заблокированным токеном."""
    # Получаем токен
    access_token = auth_client.cookies.get("access_token")
    assert access_token is not None

    # Logout (блокирует токен)
    await auth_client.post("/v1/auth/logout")

    # Пробуем получить /me с заблокированным токеном
    response = await auth_client.get(
        "/v1/auth/me",
        cookies={"access_token": access_token},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Token has been revoked"
