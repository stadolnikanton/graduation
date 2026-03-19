"""Тесты для регистрации пользователей."""

import pytest


@pytest.mark.anyio
async def test_register_success(db_connect):
    """Тест успешной регистрации пользователя."""
    response = await db_connect.post(
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

    assert response.status_code == 200
    data = response.json
    assert db_connect.cookies.get("access_token") is not None
    assert db_connect.cookies.get("refresh_token") is not None


@pytest.mark.anyio
async def test_register_email_exists(db_connect):
    """Тест регистрации с существующим email."""
    # Первая регистрация
    await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "email": "duplicate@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        },
    )

    # Вторая регистрация с тем же email
    response = await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "user2",
            "first_name": "User",
            "last_name": "Two",
            "email": "duplicate@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["error"] == "Email already registered"


@pytest.mark.anyio
async def test_register_username_exists(db_connect):
    """Тест регистрации с существующим username."""
    # Первая регистрация
    await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "unique_user",
            "first_name": "User",
            "last_name": "One",
            "email": "user1@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        },
    )

    # Вторая регистрация с тем же username
    response = await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "unique_user",
            "first_name": "User",
            "last_name": "Two",
            "email": "user2@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["error"] == "Username already registered"
