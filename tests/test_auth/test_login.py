"""Тесты для входа пользователей."""

import pytest


@pytest.mark.anyio
async def test_login_success_by_email(db_connect):
    """Тест успешного входа по email."""
    # Регистрация
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

    # Вход по email
    response = await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert db_connect.cookies.get("access_token") is not None
    assert db_connect.cookies.get("refresh_token") is not None


@pytest.mark.anyio
async def test_login_success_by_username(db_connect):
    """Тест успешного входа по username."""
    # Регистрация
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

    # Вход по username
    response = await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "test_user",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_login_not_found(db_connect):
    """Тест входа с несуществующим пользователем."""
    response = await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "nonexistent@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert data["error"] == "Invalid credentials"


@pytest.mark.anyio
async def test_login_wrong_password(db_connect):
    """Тест входа с неправильным паролем."""
    # Регистрация
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

    # Вход с неправильным паролем
    response = await db_connect.post(
        "/v1/auth/login",
        json={
            "username_or_email": "test@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert data["error"] == "Invalid credentials"
