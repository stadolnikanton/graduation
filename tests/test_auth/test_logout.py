"""Тесты для logout."""

import pytest


@pytest.mark.anyio
async def test_logout_success(auth_client):
    """Тест успешного logout."""
    response = await auth_client.post("/v1/auth/logout")

    assert response.status_code == 200
    assert auth_client.cookies.get("access_token") is None
    assert auth_client.cookies.get("refresh_token") is None


@pytest.mark.anyio
async def test_logout_blacklist(auth_client):
    """Тест что токены добавляются в blacklist после logout."""
    # Получаем токены до logout
    old_access = auth_client.cookies.get("access_token")
    assert old_access is not None

    # Logout
    response = await auth_client.post("/v1/auth/logout")
    assert response.status_code == 200

    # Пробуем сделать запрос с старым токеном (должен быть 401)
    response = await auth_client.get(
        "/v1/auth/me",
        cookies={"access_token": old_access},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Token has been revoked"
